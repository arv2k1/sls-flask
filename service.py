from calendar import c
import json
import time
from repo import UsersRepo, ScheduledLoadsRepo

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

        loads = ScheduledLoadsRepo.findAll(currentUserId)

        return loads






def getRelayStatus(espId):
    num = 0
    with open('temp.txt', 'r') as file:
        num = int(file.readline())

    with open('temp.txt', 'w') as file:
        file.write(str(1 - num))

    return { 'relay-status' : [num] * 2}


def saveMeterReadings(espId, meterReadings):

    jsonStr = ''

    with open('meterReadings.json', 'r') as file:

        mrJson = json.load(file)
        
        timeInMillis = time.time_ns()

        mrJson[str(espId)]["scheduled-meter"][str(timeInMillis)] = meterReadings['scheduled-meter']
        mrJson[str(espId)]["regular-meter"][str(timeInMillis)] = meterReadings['regular-meter']

        jsonStr = json.dumps(mrJson, indent=4)

    with open('meterReadings.json', 'w') as file:
        file.write(jsonStr)

def getMeterReadings(houseId):
    espId = houseId

    meterReading = {}
    
    with open('meterReadings.json', 'r') as file:
    
        meterReadingsJson = json.load(file)

        curHouseJson = meterReadingsJson[str(espId)]
        
        schedJson = curHouseJson['scheduled-meter']
        regularJson = curHouseJson['regular-meter']
        
        lastSchedReadingTime = max([key for key in schedJson.keys()])
        lastRegularReadingTime = max([key for key in regularJson.keys()])
        
        lastSchedReading = schedJson[lastSchedReadingTime]
        lastRegularReading = regularJson[lastRegularReadingTime]

        meterReading['scheduled-meter'] = lastSchedReading
        meterReading['regular-meter'] = lastRegularReading

    return meterReading
