import sqlite3 as sql
import time
from datetime import datetime

create_users_table = '''
    create table users (
        id integer primary key not null,
        name text not null, 
        password text not null,
        role text not null
    )
'''

insert_admin_user = '''
    insert into users(id, name, password, role) values (10001, 'admin', 'admin@123', 'ADMIN')
'''

create_schedloads_table = '''
    create table scheduledloads (
        id integer primary key not null,
        load integer not null, 
        start_after_time integer,
        end_before_time integer,
        duration integer not null,
        priority default 5 integer,
        relay integer not null,
        status integer default 0 not null,
        start_time integer,
        end_time integer,
        created_by integer
    )
'''

create_meter_readings_table = '''
    create table meter_readings (
        id integer primary key not null,
        voltage real,
        current real,
        pf real,
        frequency real,
        power real,
        energy real,
        esp_id not null,
        meter_type not null,
        time_of_reading integer not null
    )
'''

create_esp_id_consumer_id_rel_table = '''
    create table esp_id_consumer_id_rel (
        esp_id integer not null,
        consumer_id integer not null
    )
'''

init_queries = [create_users_table, insert_admin_user, create_schedloads_table, create_meter_readings_table, create_esp_id_consumer_id_rel_table]

def initDB():
    conn = sql.connect('sls.db')
    for q in init_queries:
        conn.execute(q)
        conn.commit()
    conn.close()


class UsersRepo:

    def findById(id):
        with sql.connect('sls.db') as conn:
            try:
                cursor = conn.execute("SELECT * FROM users WHERE id = ?", (id,))
                users = [UsersRepo.mapRowToUserDict(row) for row in cursor]
                return users[0]
            except Exception as e:
                print('Exception in Users::findById => ', e)
                return None

    def findAll(currentUserId):
        with sql.connect('sls.db') as conn:
            try:
                cursor = conn.execute("SELECT * FROM USERS")
                users = [UsersRepo.mapRowToUserDict(row) for row in cursor]
                return users
            except Exception as e:
                print('Exception in Users::findAll => ', e)
                return []

    def save(user):
        with sql.connect('sls.db') as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO USERS('name', 'password', 'role') VALUES (?, ?, ?)", (user['name'], user['password'], user['role'] if 'role' in user else 'CONSUMER'))
                conn.commit()
                return cursor.lastrowid
            except Exception as e:
                print('Exception in Users::save => ', e)
                return None
        
    def mapRowToUserDict(row):
        return {
            'id': row[0],
            'name': row[1],
            'password': row[2],
            'role': row[3]
        }

class ScheduledLoadsRepo:

    def findAll(currentUserId):
        with sql.connect('sls.db') as conn:
            try:
                cursor = conn.execute("SELECT * FROM scheduledloads WHERE created_by = ? ORDER BY id DESC", (currentUserId,))
                schedLoads = [ScheduledLoadsRepo.mapRowToSchedLoadDict(row) for row in cursor]
                return schedLoads
            except Exception as e:
                print('Exception in ScheduledLoadsRepo::findAll => ', e)
                return []

    def findById(id, currentUserId):
        with sql.connect('sls.db') as conn:
            try:
                cursor = conn.execute("SELECT * FROM scheduledloads WHERE id = ? AND created_by = ?", (id, currentUserId))
                schedLoads = [ScheduledLoadsRepo.mapRowToSchedLoadDict(row) for row in cursor]
                return schedLoads[0]
            except Exception as e:
                print('Exception in ScheduledLoadsRepo::findById => ', e)
                return None

    def findAllSchedulable(currentUserId, relayId):
        now = int(time.time_ns() / 1e6)
        with sql.connect('sls.db') as conn:
            try:
                q = '''
                    SELECT * FROM scheduledloads
                    WHERE 
                        created_by = ? AND
                        start_time IS NULL AND 
                        end_time IS NULL AND
                        relay = ? AND
                        start_after_time <= ? AND
                        (end_before_time > ? OR end_before_time IS NULL)
                    ORDER BY priority DESC
                '''
                
                cursor = conn.execute(q, (currentUserId, relayId, now, now))
                schedLoads = [ScheduledLoadsRepo.mapRowToSchedLoadDict(row) for row in cursor]

                print(schedLoads)

                return schedLoads
            except Exception as e:
                print('Exception in ScheduledLoadsRepo::findAllSchedulable => ', e)
                return []

    def save(schedLoad, currentUserId):
        with sql.connect('sls.db') as conn:
            try:
                cursor = conn.cursor()
                values = tuple(schedLoad.values()) + (currentUserId,)

                q = "INSERT INTO scheduledloads(" 
                q += ', '.join(list(map(lambda x: f"'{x}'", list(schedLoad.keys()) + ['created_by'])))
                q += ") VALUES ("
                q += ', '.join(['?'] * (len(schedLoad.keys()) + 1))
                q += ")"

                cursor.execute(q, values)
                conn.commit()
                return cursor.lastrowid
            except Exception as e:
                print('Exception in ScheduledLoadsRepo::save => ', e)
                return None

    def updateRunningStatus():

        now = int(time.time_ns() / 1e6)

        with sql.connect('sls.db') as conn:
            try:
                conn.execute("UPDATE scheduledloads SET status = 1 WHERE start_time IS NOT NULL AND end_time IS NOT NULL AND start_time <= ? AND end_time >= ?", (now, now))
                conn.commit()
                conn.execute("UPDATE scheduledloads SET status = 2 WHERE start_time IS NOT NULL AND end_time IS NOT NULL AND start_time <= ? AND end_time <= ?", (now, now))
                conn.commit()
                conn.execute("UPDATE scheduledloads SET status = -1 WHERE start_time IS NULL AND end_time IS NULL AND end_before_time <= ?", (now, ))
                conn.commit()
                return True
            except Exception as e:
                print('Exception in ScheduledLoadsRepo::updateRunningStatus => ', e)
                return False

    def update(schedLoadId, startTime, endTime):
        with sql.connect('sls.db') as conn:
            try:
                conn.execute('UPDATE scheduledloads SET start_time = ?, end_time = ?, status = 1 WHERE id = ?', (startTime, endTime, schedLoadId))
                conn.commit()
                return True
            except Exception as e:
                print('Exception in ScheduledLoadsRepo::update => ', e)
                return False

    def mapRowToSchedLoadDict(row):
        return {
            'id': row[0],
            'load': row[1],
            'start_after_time': row[2],
            'end_before_time': row[3],
            'duration': row[4],
            'priority': row[5],
            'relay': row[6],
            'status': row[7],
            'start_time': row[8],
            'end_time': row[9]
        }

class MeterReadingsRepo:

    def findByMaxTimeForGivenMeterType(meterType, consumerId):
        espId = EspIdConsumerIdRelRepo.findEspIdByConsumerId(consumerId)
        with sql.connect('sls.db') as conn:
            try:
                cursor = conn.execute("SELECT * FROM meter_readings WHERE esp_id = ? AND meter_type = ? AND voltage IS NOT null ORDER BY time_of_reading DESC LIMIT 1", (espId, meterType))
                meterReading = [MeterReadingsRepo.mapRowToMeterReadingDict(row) for row in cursor][0]
                return meterReading
            except Exception as e:
                print('Exception in MeterReadingsRepo::findByMaxTimeForGivenMeterType => ', e)
                return None


    def save(meterReading, meterType, espId):
        with sql.connect('sls.db') as conn:
            try:
                values = tuple(meterReading.values()) + (espId, meterType, int(time.time_ns()/1e6))

                q = "INSERT INTO meter_readings(" 
                q += ', '.join(list(map(lambda x: f"'{x}'", list(meterReading.keys()) + ['esp_id', 'meter_type', 'time_of_reading'])))
                q += ") VALUES ("
                q += ', '.join(['?'] * (len(meterReading.keys()) + 3))
                q += ")"

                cursor = conn.execute(q, values)
                return cursor.lastrowid
            except Exception as e:
                print('Exception in EspIdConsumerIdRelRepo::save => ', e)
                return None

    def mapRowToMeterReadingDict(row):
        
        # ns = row[9]
        # secs = ns / 1e9
        # dt = datetime.fromtimestamp(secs)
        # text = dt.strftime('%d-%m-%Y %H:%M:%S')

        # text = int(ns / 1e6)

        return {
            'voltage': row[1],
            'current': row[2],
            'pf': row[3],
            'frequency': row[4],
            'power': row[5],
            'energy': row[6],
            'time_of_reading': row[9]
        }

class EspIdConsumerIdRelRepo:

    def findEspIdByConsumerId(consumerId):
        with sql.connect('sls.db') as conn:
            try:
                cursor = conn.execute("SELECT * FROM esp_id_consumer_id_rel WHERE consumer_id = ?", (consumerId,))
                for row in cursor:
                    return row[0]
                return None
            except Exception as e:
                print('Exception in EspIdConsumerIdRelRepo::findEspIdByConsumerId => ', e)
                return None

    def findConsumerIdByEspId(espId):
        with sql.connect('sls.db') as conn:
            try:
                cursor = conn.execute("SELECT * FROM esp_id_consumer_id_rel WHERE esp_id = ?", (espId,))
                for row in cursor:
                    return row[1]
                return None
            except Exception as e:
                print('Exception in EspIdConsumerIdRelRepo::findConsumerIdByEspId => ', e)
                return None

    def save(espId, consumerId):
        with sql.connect('sls.db') as conn:
            try:
                conn.execute("INSERT INTO esp_id_consumer_id_rel values(?, ?)", (espId, consumerId))
                return True
            except Exception as e:
                print('Exception in EspIdConsumerIdRelRepo::save => ', e)
                return False



if __name__ == '__main__':

    print('======= SLS Repo ========')

    # initDB()

    # UsersRepo.save({'name':'Harish', 'password':'1234'})
    # UsersRepo.save({'name':'Priyan', 'password':'1234'})
    # UsersRepo.save({'name':'Aravind', 'password':'1234'})
    # UsersRepo.save({'name':'Vasanth', 'password':'1234'})

    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10002)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10002)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10002)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10002)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10002)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10002)

    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':None, 'end_before_time':None, 'duration':60, 'priority':None, 'relay':1}, 10002)
    # ScheduledLoadsRepo.save({'load':10, 'duration':60, 'relay':1}, 10002)

    # print(ScheduledLoadsRepo.findAll(10002))

    # EspIdConsumerIdRelRepo.save(1, 10002)
    # EspIdConsumerIdRelRepo.save(2, 10003)

    # print(EspIdConsumerIdRelRepo.findEspIdByConsumerId(10002))

    # print(MeterReadingsRepo.findByMaxTimeForGivenMeterType(0, 10002))

    # print(len(ScheduledLoadsRepo.findAllSchedulable(10003, 2)))

    # ScheduledLoadsRepo.update(95, 123, 123)