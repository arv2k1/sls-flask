from repo import UsersRepo, ScheduledLoadsRepo, MeterReadingsRepo

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
        
        
        

def getRelayStatus(espId):
    num = 0
    with open('temp.txt', 'r') as file:
        num = int(file.readline())

    with open('temp.txt', 'w') as file:
        file.write(str(1 - num))

    return { 'relay-status' : [num] * 2}