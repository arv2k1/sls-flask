from flask import Flask, Response, make_response, jsonify, request
from service import UsersService, ScheduledLoadService, MeterReadingsService
import service

app = Flask(__name__, static_url_path='')






# User Controller
@app.route('/api/v1/users/current-user')
def getCurrentUser():
    userIdFromCookie = request.cookies.get('userId')
    if userIdFromCookie:
        user = UsersService.getUser(userIdFromCookie, None)
        if user:
            return {'user': user}
        else:
            return make_response({ 'code':'INVALID_DATA', 'status':'error', 'message':'User not found', 'details':{} }, 400)
    else:
        return make_response({'code':'MANDATORY_NOT_FOUND', 'status':'error', 'message':'Invalid cookie', 'details':{} }, 400)

@app.route('/api/v1/login', methods = ['POST'])
def login():
    userFromReq = request.get_json()['user']

    if not userFromReq or not userFromReq['id'] or not userFromReq['password']:
        return make_response({'code':'MANDATORY_NOT_FOUND', 'status':'error', 'message':'Invalid request body', 'details':{} }, 400)

    user = UsersService.getUser(userFromReq['id'], userFromReq['password'], userFromReq['role'] if 'role' in userFromReq else 'CONSUMER')

    if user:
        resp = make_response(jsonify({'user': user}))
        resp.set_cookie('userId', str(user['id']))
        return resp
    return make_response({ 'code':'INVALID_DATA', 'status':'error', 'message':'User not found', 'details':{} }, 400)
        
@app.route('/api/v1/sign-up', methods = ['POST'])
def signUp():
    userFromReq = request.get_json()['user']

    if not userFromReq or not userFromReq['name'] or not userFromReq['consumer_id'] or not userFromReq['password'] :
        return make_response({'code':'MANDATORY_NOT_FOUND', 'status':'error', 'message':'Invalid request body', 'details':{} }, 400)

    user = UsersService.getUser(userFromReq['id'])

    if user:
        resp = make_response({'user': user})
        resp.set_cookie('userId', user['id'])
        return resp
    return make_response({ 'code':'INVALID_DATA', 'status':'error', 'message':'User not found', 'details':{} }, 400)
    
    
    

# Scheduled Loads
@app.route('/api/v1/scheduled-loads', methods=['GET', 'POST'])
def getScheduledLoads():
    userIdFromCookie = request.cookies.get('userId')
    if request.method == 'GET':
        if userIdFromCookie:
            loads = ScheduledLoadService.getScheduledLoads(userIdFromCookie)    
            return {'scheduled-loads': loads}
        else:
            return make_response({ 'code':'INVALID_DATA', 'status':'error', 'message':'Invalid cookie', 'details':{} }, 400)
    else:
        schedLoad = request.get_json()['scheduled_load'] if 'scheduled_load' in request.get_json() else None
        if schedLoad:
            schedLoadId = ScheduledLoadService.scheduleNewLoad(schedLoad, userIdFromCookie)
            if schedLoadId:
                return make_response({'code':'SUCCESS', 'status':'success', 'message':'Scheduled successfully', 'details':{'id':schedLoadId}}, 201)
            return make_response({ 'code':'INVALID_DATA', 'status':'error', 'message':'Failed to schedule load', 'details':{} }, 400)
        else:
            return make_response({ 'code':'MANDATORY_NOT_FOUND', 'status':'error', 'message':'Invalid json body', 'details':{} }, 400)
            
            
            
        

# Meter readings
@app.route('/api/v1/meter-readings')
def getMeterReadings():
    userIdFromCookie = request.cookies.get('userId')
    if userIdFromCookie:
        return MeterReadingsService.getLatestReading(userIdFromCookie)
    else:
        return make_response({ 'code':'INVALID_DATA', 'status':'error', 'message':'Invalid cookie', 'details':{} }, 400)

    
    
    

# ESP Api's
@app.route('/<int:espId>/relay-status')
def getRelayStatus(espId):
    return ScheduledLoadService.getRelayStatus(espId)

@app.route('/<int:espId>/meter-readings', methods = ['POST'])
def postMeterReadings(espId):
    meterReadings = request.get_json()
    # print(json.dumps(meterReadings, indent=4))
    res = MeterReadingsService.saveMeterReadings(meterReadings, espId)
    return make_response(res, 201)

@app.route('/log', methods = ['POST'])
def postLogMessage():
    msg = request.data.decode('UTF-8')  
    print('>>> ' + msg)
    return Response(status=200)

    


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)