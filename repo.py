import sqlite3 as sql

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

init_queries = [create_users_table, insert_admin_user, create_schedloads_table]

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
                cursor = conn.execute("SELECT * FROM scheduledloads WHERE created_by = ?", (currentUserId,))
                schedLoads = [ScheduledLoadsRepo.mapRowToSchedLoadDict(row) for row in cursor]
                return schedLoads
            except Exception as e:
                print('Exception in ScheduledLoadsRepo::findAll => ', e)
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

    def update(schedLoadId, startTime, endTime, status, currentUserId):
        return
        with sql.connect('sls.db') as conn:
            try:
                cursor = conn.cursor()
                cursor.execute('', ())
                conn.commit()
                return cursor.lastrowid
            except Exception as e:
                print('Exception in ScheduledLoadsRepo::save => ', e)
                return None

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

if __name__ == '__main__':

    print('======= SLS Repo ========')

    # initDB()

    # UsersRepo.save({'name':'Harish', 'password':'1234'})
    # UsersRepo.save({'name':'Priyan', 'password':'1234'})
    # UsersRepo.save({'name':'Aravind', 'password':'1234'})
    # UsersRepo.save({'name':'Vasanth', 'password':'1234'})

    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10002)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10002)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10002)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10002)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10002)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10002)

    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    ScheduledLoadsRepo.save({'load':10, 'start_after_time':1654687800000, 'end_before_time':1654702200000, 'duration':60, 'priority':5, 'relay':1}, 10003)
    
    # ScheduledLoadsRepo.save({'load':10, 'start_after_time':None, 'end_before_time':None, 'duration':60, 'priority':None, 'relay':1}, 10002)
    # ScheduledLoadsRepo.save({'load':10, 'duration':60, 'relay':1}, 10002)

    # print(ScheduledLoadsRepo.findAll(10002))

