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

    def scheduleNewLoad(load, currentUserId):

        return ScheduledLoadsRepo.save(load, currentUserId)

    def getRelayStatus(espId):

        consumerId = EspIdConsumerIdRelRepo.findConsumerIdByEspId(espId)

        runningLoads = ScheduledLoadService.__getRunningLoads(consumerId)

        status = [0] * 2

        for load in runningLoads:
            relay = load['relay']
            status[relay] = 1
        
        return { 'relay-status' : status }

    def __getRunningLoads(consumerId):
        
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
        
        return res