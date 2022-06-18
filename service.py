from time import time_ns
from repo import EspIdConsumerIdRelRepo, UsersRepo, ScheduledLoadsRepo, MeterReadingsRepo

# =========== Users ===========
class UsersService:

    def getUser(id, password, role='CONSUMER'):
        try:
            user = UsersRepo.findById(id)
            if password and user['password'] != password or user['role'] != role:
                return None
            user.pop('password')
            return user
        except Exception as e:
            return None
    
    def saveUser(name, password):
        try:
            id = UsersRepo.save({'name': name, 'password': password})
            return id
        except Exception as e:
            return None



# =========== Scheduled Loads ===========

class ScheduledLoadService:

    def getScheduledLoads(currentUserId):

        return ScheduledLoadsRepo.findAll(currentUserId)

    def getScheduledLoad(loadId, currentUserId):

        return ScheduledLoadsRepo.findById(loadId, currentUserId)

    def scheduleNewLoad(load, currentUserId):

        return ScheduledLoadsRepo.save(load, currentUserId)

    def getRelayStatus(espId):

        consumerId = EspIdConsumerIdRelRepo.findConsumerIdByEspId(espId)

        runningLoads = ScheduledLoadService._getRunningLoads(consumerId)

        status = [0] * 2

        for load in runningLoads:
            relay = load['relay']
            status[relay-1] = 1
        
        return { 'relay-status' : status }

    def _getRunningLoads(consumerId):
        
        ScheduledLoadsRepo.updateRunningStatus()

        loads = ScheduledLoadsRepo.findAll(consumerId)
        runningLoads = list(filter(lambda load: load['status'] == 1, loads))
        
        return runningLoads
        

# =========== Meter readings ===========
class MeterReadingsService:
    SCHEDULED_METER = 0
    REGULAR_METER = 1

    def getLatestReading(currentUserId):
        schedReading = MeterReadingsRepo.findByMaxTimeForGivenMeterType(MeterReadingsService.SCHEDULED_METER, currentUserId)
        regReading = MeterReadingsRepo.findByMaxTimeForGivenMeterType(MeterReadingsService.REGULAR_METER, currentUserId)

        return {
            'scheduled_meter': schedReading,
            'regular_meter': regReading
        }

    def saveMeterReadings(meterReadings, espId):
        res = {}
        if 'scheduled_meter' in meterReadings:
            schedReading = meterReadings['scheduled_meter']
            id = MeterReadingsRepo.save(schedReading, MeterReadingsService.SCHEDULED_METER, espId)
            res['scheduled_meter'] = id

        if 'regular_meter' in meterReadings:
            schedReading = meterReadings['regular_meter']
            id = MeterReadingsRepo.save(schedReading, MeterReadingsService.REGULAR_METER, espId)
            res['regular_meter'] = id
        
        SchedulerService.schedule(EspIdConsumerIdRelRepo.findConsumerIdByEspId(espId))

        return res


# ========= Scheduler service ==========
class SchedulerService:

    def getCurrentUsage(currentUserId):
        try:
            mr = MeterReadingsService.getLatestReading(currentUserId)
            
            smr = mr['scheduled_meter']
            rmr = mr['regular_meter']
            
            smTime = smr['time_of_reading']
            rmTime = rmr['time_of_reading']

            now = int(time_ns()/1e6)

            noticePeriod = 30 * 1000 # 30s in ms

            smp = smr['power'] if now - smTime <= noticePeriod else 0
            rmp = rmr['power'] if now - rmTime <= noticePeriod else 0

            usage = smp + rmp

            return usage
        except:
            return 0


    def schedule(currentUserId):

        espId = EspIdConsumerIdRelRepo.findEspIdByConsumerId(currentUserId)

        production = 20
        usage = SchedulerService.getCurrentUsage(currentUserId)
        remaining = production - usage

        print('Usage: ' + str(usage))
        print('Remaining: ' + str(remaining))


        for relay in range(1, 3):
            print('========= Scheduling for house: ' + str(espId) + ', relay: ' + str(relay) + ' ==========')

            # If already load running in this relay skip scheduling for this relay
            curRelayStatus = ScheduledLoadService.getRelayStatus(espId)['relay-status'][relay-1] 

            if curRelayStatus == 1:
                print('Relay is busy')
                continue

            # loads that can be run by :relay right now
            loads = ScheduledLoadsRepo.findAllSchedulable(currentUserId, relay)

            # loads that can be run with the remaining capacity
            loads = list(filter(lambda x: x['load'] <= remaining, loads))

            print('Eligible number of loads => ' + str(len(loads)))

            if(len(loads) > 0):
                chosenLoad = loads[0]
                print('>>> Chosen load >>>')
                print(chosenLoad)
                remaining -= chosenLoad['load']
                now = int(time_ns()/1e6)
                ScheduledLoadsRepo.update(chosenLoad['id'], now, now + chosenLoad['duration'] * 60 * 1000)