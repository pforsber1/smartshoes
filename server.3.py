from gpiozero import PWMOutputDevice
import bluetooth
import multiprocessing
import RPi.GPIO as GPIO
import time
import random
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(22,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(24,GPIO.OUT)
GPIO.setup(25,GPIO.OUT)
GPIO.setup(5,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
motor1 = GPIO.PWM(17,1000)
motor2 = GPIO.PWM(22,1000)
motor3 = GPIO.PWM(23,1000)
motor4 = GPIO.PWM(24,1000)
motor5 = GPIO.PWM(25,1000)
motor1.start(0)
motor2.start(0)
motor3.start(0)
motor4.start(0)
motor5.start(0)
count = -1
gp1 = [motor1,motor2,motor3]
gp2 = [motor1,motor2,motor4]
gp3 = [motor1,motor2,motor5]
gp4 = [motor1,motor3,motor4]
gp5 = [motor1,motor3,motor5]
gp6 = [motor1,motor4,motor5]
gp7 = [motor2,motor3,motor4]
gp8 = [motor2,motor3,motor5]
gp9 = [motor2,motor4,motor5]
gp10 = [motor3,motor4,motor5]
randnum = 0
global data
data = 0
buffer = 0
previousData = 0





#///////////////////// Functions //////////////////////////////////
def motors_set(level):
    motor1.ChangeDutyCycle(level)
    motor2.ChangeDutyCycle(level)
    motor3.ChangeDutyCycle(level)
    motor4.ChangeDutyCycle(level)
    motor5.ChangeDutyCycle(level)
    
def button_callback(channel):
    clientSlave.send("0")
    global data
    data = data
    print("Button was pushed")
    print("data:",data)
    if data == "2": #if currently flashing, turn off
        print("you are hereeeee")
        p1.terminate()
        Off([motor1,motor2,motor3,motor4,motor5])
    elif data == "3": #if currently random, turn off
        p2.terminate()
        Off([motor1,motor2,motor3,motor4,motor5])
    else:
        Off([motor1,motor2,motor3,motor4,motor5])
    global count
    count = count+1
    print("COUNT:",count)
    if count == 0:
        motors_set(0)
        clientSlave.send("5")
    elif count == 1:
        motors_set(25)
        clientSlave.send("6")
    elif count == 2:
        motors_set(50)
        clientSlave.send("7")
    elif count == 3:
        motors_set(75)
        clientSlave.send("8")
    elif count == 4:
        motors_set(100)
        clientSlave.send("9")
    else:
        count = 0
        motors_set(0)
        clientSlave.send("0")
        print("Counter Reset", count)
    data = "4"
        
def On(cluster):
    for x in cluster:
        x.stop()
        x.start(50)

def Off(cluster):
    for x in cluster:
        x.stop()
        x.start(0)

def groupFlash(group):
    On(group)
    time.sleep(.5)
    Off(group)




#//////////////////// Multiprocessing Processes (modes) ////////////////////////
def flashing():
    while True:
        motor1.start(0)
        motor2.start(0)
        motor3.start(0)
        motor4.start(0)
        motor5.start(0)
        for x in range(75):
            motor1.ChangeDutyCycle(x)
            motor2.ChangeDutyCycle(x)
            motor3.ChangeDutyCycle(x)
            motor4.ChangeDutyCycle(x)
            motor5.ChangeDutyCycle(x)
        time.sleep(.3)
        for x in range(75):
            motor1.ChangeDutyCycle(75-x)
            motor2.ChangeDutyCycle(75-x)
            motor3.ChangeDutyCycle(75-x)
            motor4.ChangeDutyCycle(75-x)
            motor5.ChangeDutyCycle(75-x)
        time.sleep(.3)
        
def randomFlashing():
    while True:
        motor1.start(0)
        motor2.start(0)
        motor3.start(0)
        motor4.start(0)
        motor5.start(0)
        r1 = random.randrange(1, 10)
        if r1 == 1:
            groupFlash(gp1)
        if r1 == 2:
            groupFlash(gp2)
        if r1 == 3:
            groupFlash(gp3)
        if r1 == 4:
            groupFlash(gp4)
        if r1 == 5:
            groupFlash(gp5)
        if r1 == 6:
            groupFlash(gp6)
        if r1 == 7:
            groupFlash(gp7)
        if r1 == 8:
            groupFlash(gp8)
        if r1 == 9:
            groupFlash(gp9)
        if r1 == 10:
            groupFlash(gp10)
    



#///////////////////// Bluetooth Server ///////////////////////////
host = ""
port = 1        # Raspberry Pi uses port 1 for Bluetooth Communication
# Creaitng Socket Bluetooth RFCOMM communication

server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
print('Bluetooth Socket Created')
GPIO.add_event_detect(5,GPIO.RISING,callback=button_callback,bouncetime=200)
try:
        server.bind((host, port))
        print("Bluetooth Binding Completed")
except:
        print("Bluetooth Binding Failed")
server.listen(2) # Two connections at a time
# Server accepts the clients request and assigns a mac address.
clientSlave, addressSlave = server.accept()
print("Connected To", addressSlave)
print("Client:", clientSlave)
client, address = server.accept()
print("Connected To", address)
print("Client:", client)


try:
    On([motor1,motor2,motor3,motor4,motor5])
    time.sleep(.1)
    Off([motor1,motor2,motor3,motor4,motor5])
    while True:
        buffer = client.recv(1024)
        clientSlave.send(buffer)
        if (data != buffer):
            previousData = data
            data = buffer
            count = 0
            
            
            
#/////////// ON //////////////////////////////////////////////////////
            if data == "1":
                if previousData == "2":
                    p1.terminate()
                    Off([motor1,motor2,motor3,motor4,motor5])
                elif previousData == "3":
                    p2.terminate()
                    Off([motor1,motor2,motor3,motor4,motor5])
                send_data = "Motors On"
                On([motor1,motor2,motor3,motor4,motor5])
                
                
                
#/////////// OFF /////////////////////////////////////////////////////
            elif data == "0":
                if previousData == "2":
                    send_data = "NO Flashing"
                    p1.terminate()
                    Off([motor1,motor2,motor3,motor4,motor5])
                elif previousData == "3":
                    send_data = "NO Random"
                    p2.terminate()
                    Off([motor1,motor2,motor3,motor4,motor5])
                else:
                    send_data = "Motors Off"
                    Off([motor1,motor2,motor3,motor4,motor5])
                    
                    
                    
#/////////// FLASHING ////////////////////////////////////////////////
            elif data == "2":
                send_data = "Flashing"
                try:
                    if previousData == "3":
                        p2.terminate()
                    motor1.stop()
                    motor2.stop()
                    motor3.stop()
                    motor4.stop()
                    motor5.stop()
                    p1 = multiprocessing.Process(target=flashing)
                    p1.start()
                except:
                    send_data = "Flashing did not work=============="
                    
                    
                    
#/////////// RANDOM //////////////////////////////////////////////////
            elif data == "3":
                send_data = "Random"
                try:
                    if previousData == "2":
                        p1.terminate()
                    motor1.stop()
                    motor2.stop()
                    motor3.stop()
                    motor4.stop()
                    motor5.stop()
                    p2 = multiprocessing.Process(target=randomFlashing)
                    p2.start()
                except:
                    send_data = "Random did not work================="
            
            
            #//////// NOTE ///////
            # When adding another mode, data == "10" since 5-9 are used on client side
            #//////// NOTE ///////
            
            
            else:
                send_data = "INVALID INPUT"
                # Sending the data.
            print(send_data)
            client.send(send_data)

except:
    # Making all the output pins LOW
    GPIO.cleanup()
    print("Terminating...")
    # Terminating the threads
    p1.terminate()
    p2.terminate()
    # Closing the client and server connection
    client.close()
    server.close()





