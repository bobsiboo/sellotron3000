##################
# sellotron3000 #
##################
#
#
#
#
# V 0.0.1 (alpha)
#



#Current setup assumes the following pin usage
#If other pins are used the code should be updated
#GPIO 13 - to  relais (solenoid valve water)
#GPIO 26 - input coin counter
#GPIO 19 - watermeter
#
#

import RPi.GPIO as GPIO
import os
import logging
import multiprocessing 
from multiprocessing import Process, Value
import sys
import datetime

manager = multiprocessing.Manager()
GPIO.setwarnings(False)
#Setting GPIO pins to be used, Change here if setup requires other pins
GPIO_COIN = 26								#Set GPIO for coincounter
GPIO_RELAIS = 16							#Set GPIO for relais
GPIO_METER = 19								#Set GPIO for watermeter

#Declaring GPIO  Pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_COIN, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)		#set coin as coin input
GPIO.setup(GPIO_RELAIS, GPIO.OUT)					#Set relais as output
GPIO.setup(GPIO_METER, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)		#Set meter as input
LOGFILE = '/var/log/sellotron3000'
COINFILE = '/var/log/sellotroncoin'
METERFILE = '/var/log/sellotronmeter'
PPC = 10                 #pulse per credit (to be put in formula) still test value
RUN = 1
#Uncomment if vallues need to be set to 0 on boot
#f = open(COINFILE, 'w')		       				#Set value to 0
#f.write((str(0)+ '\n'))                         # 
#f.write((str(datetime.datetime.now())+ '\n'))   # 
#f = open(METERFILE, 'w')		       				#Set value to 0
#f.write((str(0)+ '\n'))                         # 
#f.write((str(datetime.datetime.now())+ '\n'))   # 

def coinInput(): #listen to coin input
    global GPIO_COIN
    global GPIO_METER
    global GPIO_RELAIS
    while True:
        GPIO.wait_for_edge(GPIO_COIN, GPIO.RISING)
        #add credit to credit counter

        #logfile
        try:
            f = open(COINFILE, 'r')                   # open for reading.
            value = int(f.readline().rstrip())  
                      # read the first line; it should be an integer value
            print ("ok")
        except:
            value = 0  # if something went wrong, reset to 0
            print ("error")
        f.close()
        print ("original value")
        print ((str(value) + '\n'))
        value +=1
        f = open(COINFILE, 'w')		       			    #open file to append
        f.write((str(value)+ '\n'))                   # the value
        f.write((str(datetime.datetime.now())+ '\n'))   # timestamp
        f.close()
        print ((str(datetime.datetime.now())))
        print ("1 credit added, total credits: ")
        print ((str(value) + '\n'))
        f = open(LOGFILE, 'a')		       				#open file to append
        f.write((str(datetime.datetime.now())))			#log datetime
        f.write(":  1 credit added, Total credits: ")	#add credit to log
        f.write((str(value+1)+ '\n'))					#total credits to log
        f.close()
        GPIO.wait_for_edge(GPIO_COIN, GPIO.FALLING)

def meterInput(): #listen to meter input
    global GPIO_COIN
    global GPIO_METER
    global GPIO_RELAIS
    while True:
        GPIO.wait_for_edge(GPIO_METER, GPIO.RISING)
        try:
            f = open(METERFILE, 'r')                  # open for reading. If it does not exist, create it
            value = int(f.readline().rstrip())          # read the first line; it should be an integer value
        except:
            value = 0                                   # if something went wrong, reset to 0
        f = open(METERFILE, 'w')		       			    #open file to append
        f.write((str(value+1)+ '\n'))                   # the value
        f.write((str(datetime.datetime.now())+ '\n'))   # timestamp
        f.close()
        print ((str(datetime.datetime.now())))
        print ("meter increaded, new total:")
        print ((str(value+1) + '\n'))
        GPIO.wait_for_edge(GPIO_METER, GPIO.FALLING)

def relaiscontroll ():
    global GPIO_COIN
    global GPIO_METER
    global GPIO_RELAIS
    PPC = 10
    RUN = 1
    RELAIS_OPEN = 1
    while RUN ==1:
        try:
            f = open(COINFILE, 'r')                   # open for reading. If it does not exist, create it
            CREDITS = int(f.readline().rstrip())          # read the first line; it should be an integer value
        except:
            CREDITS = 0  
        f.close()
        #print ((str(CREDITS) + '\n'))

        while CREDITS >= 1:
            GPIO.output(GPIO_RELAIS, GPIO.HIGH)
            try:
                f = open(COINFILE, 'r')                   # open for reading. If it does not exist, create it
                CREDITS = int(f.readline().rstrip())          # read the first line; it should be an integer value
            except:
                CREDITS = 0  
            f.close()
            if RELAIS_OPEN == 0:
                RELAIS_OPEN = 1
                f = open(LOGFILE, 'a')
                f.write((str(datetime.datetime.now())))
                f.write(" Relais Open \n")
                f.close()
                print ("Relais Open ")
            #substract credits
            try:
                f = open(METERFILE, 'r')                   # open for reading. If it does not exist, create it
                METER = int(f.readline().rstrip())          # read the first line; it should be an integer value
            except:
                METER = 0             # if something went wrong, reset to 0
            f.close()
            if METER >= PPC:
                print ("1 credit consumed")
                try:
                    f = open(COINFILE, 'r')                   # open for reading.
                    COINS = int(f.readline().rstrip())  
                      # read the first line; it should be an integer value
                    #print ("ok")
                except:
                    COINS = 0  # if something went wrong, reset to 0
                    #print ("error")
                f.close()
                print ("new credit value")
                print ((str(COINS-1) + '\n'))

                f = open(COINFILE, 'w')		       			    #open file to append
                f.write((str(COINS-1)+ '\n'))                   # the value
                f.write((str(datetime.datetime.now())+ '\n'))   # timestamp
                f.close()
                METER = 0
                f = open(METERFILE, 'w')		       			    #open file to append
                f.write((str(METER)+ '\n'))                   # the value
                f.write((str(datetime.datetime.now())+ '\n'))   # timestamp
                f.close()

        while CREDITS == 0:
            GPIO.output(GPIO_RELAIS, GPIO.LOW)
            try:
                f = open(COINFILE, 'r')                   # open for reading. If it does not exist, create it
                CREDITS = int(f.readline().rstrip())          # read the first line; it should be an integer value
            except:
                CREDITS = 0  
            f.close()
            if RELAIS_OPEN == 1:
                RELAIS_OPEN = 0
                f = open(LOGFILE, 'a')
                f.write((str(datetime.datetime.now())))
                f.write(" Relais closed \n")
                f.close()
                print ("Relais closed \n")

cc = Process(name='coin-counter', target=coinInput)
mc = Process(name='meter-counter', target=meterInput)
rc = Process(name='relais-controll', target=relaiscontroll)



cc.start()
mc.start()
rc.start()
while RUN == 1: #keep allive
    RUN = 1



GPIO.cleanup()
