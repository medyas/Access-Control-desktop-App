import RPi.GPIO as GPIO
from time import sleep
import MySQLdb, datetime

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


# --------------------------------------------------- #

class Servo:
    def __init__(self, pin):
        GPIO.setmode(GPIO.BCM)
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)# yellow 
        self.servopwm = GPIO.PWM(self.pin, 50)
        self.servopwm.start(0)
        self.servopwm.ChangeDutyCycle(3)
        
    def setOpen(self):
        duty = 90 / 18.0 + 2
        GPIO.output(self.pin, True)
        self.servopwm.ChangeDutyCycle(duty)
        sleep(0.0001)

    def setClose(self):
        duty = 0 / 18.0 + 3
        GPIO.output(self.pin, True)
        self.servopwm.ChangeDutyCycle(duty)
        sleep(0.0001)

# --------------------------------------------------- #

class Led:
    def __init__(self, pin):
        GPIO.setmode(GPIO.BCM)
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        GPIO.output(self.pin, GPIO.LOW)

# --------------------------------------------------- #

class DataBase:
    def __init__(self, localhost, user, password, database):
        self.db = MySQLdb.connect(localhost, user, password, database)
        self.cursor = self.db.cursor()

    def close(self):
        self.db.close()

    def checkUID(self, uid):
        sql = "select * from employees where card_uid="+uid
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            if(len(data) == 0):
                return False, None
            return True, data
        except:
            return False, None

    def setLogin(self, uid):
        date = datetime.date.today().strftime('%Y-%m-%d')
        time = datetime.datetime.now().strftime('%H:%M:%S')
        sql = "insert into employee_logs (user_id, date, time) values("+str(uid)+", '"+date+"', '"+time+"')"
        self.cursor.execute(sql)
        self.db.commit()

    def check_block(self, uid):
        sql = "select * from blocked_employee where user_id="+str(uid)
        d = None
        date = None
        
        try:
            self.cursor.execute(sql)
            d = self.cursor.fetchall()
        except:
            return False, None, None

        if(len(d) != 0):
            data = d[len(d)-1]
        else:
            return False, None, None

        start_date = data[2] 
        end_date = data[3]
        current_date = datetime.datetime.strptime(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        
        if(current_date >= start_date and current_date <= end_date):
            return True, start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return False, None, None

# --------------------------------------------------- #
