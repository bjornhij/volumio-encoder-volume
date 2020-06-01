
import RPi.GPIO as GPIO
import threading
from time import sleep
import requests

                        # GPIO Ports
Enc_A = 25                  # Encoder input A: input GPIO 4 
Enc_B = 24                      # Encoder input B: input GPIO 14 

PLAY = 13
PREV = 12
NEXT = 6
STOP = 27

Rotary_counter = 0              # Start counting from 0
Current_A = 1                    # Assume that rotary switch is not 
Current_B = 1                    # moving while we init software

LockRotary = threading.Lock()        # create lock for rotary switch
    

# initialize interrupt handlers
def init():
    global api_session

    api_session = requests.session()

    GPIO.setwarnings(True)
    GPIO.setmode(GPIO.BCM)                    # Use BCM mode
                                            # define the Encoder switch inputs
    GPIO.setup(Enc_A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)                 
    GPIO.setup(Enc_B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.setup(PLAY, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(PREV, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(NEXT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(STOP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

  
                                            # setup callback thread for the A and B encoder 
                                            # use interrupts for all inputs
    GPIO.add_event_detect(Enc_A, GPIO.RISING, callback=rotary_interrupt)                 # NO bouncetime 
    GPIO.add_event_detect(Enc_B, GPIO.RISING, callback=rotary_interrupt)                 # NO bouncetime 

    GPIO.add_event_detect(PLAY, GPIO.RISING, callback=play_interrupt)

    GPIO.add_event_detect(STOP, GPIO.RISING, callback=stop_interrupt)


    GPIO.add_event_detect(NEXT, GPIO.RISING, callback=next_interrupt)

    GPIO.add_event_detect(PREV, GPIO.RISING, callback=previous_interrupt)

    return


def play_interrupt(arg):
   global api_session
   print("play")
   resp = api_session.get('http://localhost:3000/api/v1/commands/?cmd=play')
   return

def stop_interrupt(arg):
   global api_session
   print("stop")
   resp = api_session.get('http://localhost:3000/api/v1/commands/?cmd=stop')
   return

def previous_interrupt(arg):
   global api_session
   print("previous")
   resp = api_session.get('http://localhost:3000/api/v1/commands/?cmd=prev')
   return

def next_interrupt(arg):
   global api_session
   print("next")
   resp = api_session.get('http://localhost:3000/api/v1/commands/?cmd=next')
   return


# Rotarty encoder interrupt:
# this one is called for both inputs from rotary switch (A and B)
def rotary_interrupt(A_or_B):
    global Rotary_counter, Current_A, Current_B, LockRotary, api_session
            
                                        # read both of the switches
    Switch_A = GPIO.input(Enc_A)
    Switch_B = GPIO.input(Enc_B)
                                                    # now check if state of A or B has changed
                                                    # if not that means that bouncing caused it
    if Current_A == Switch_A and Current_B == Switch_B:        # Same interrupt as before (Bouncing)?
        return                                        # ignore interrupt!

    Current_A = Switch_A                                # remember new state
    Current_B = Switch_B                                # for next bouncing check


    if (Switch_A and Switch_B):                        # Both one active? Yes -> end of sequence
        LockRotary.acquire()                        # get lock 
        if A_or_B == Enc_B:                            # Turning direction depends on 
            direction = -1                        # which input gave last interrupt
        else:                                        # so depending on direction either
            direction = 1                        # increase or decrease counter
        LockRotary.release()                        # and release lock
    
        resp = api_session.get('http://localhost:3000/api/v1/commands/?cmd=volume&volume=%s' % ('plus' if direction == 1 else 'minus'))

        print(direction)

    return                                            # THAT'S IT

# Main loop. Demonstrate reading, direction and speed of turning left/rignt
def main():
    global Rotary_counter, LockRotary, api_session
    

    Volume = 0                                    # Current Volume    
    NewCounter = 0                                # for faster reading with locks
                        

    init()                                        # Init interrupts, GPIO, ...
                
    while True :                                # start test 
        sleep(1)                                # sleep 100 msec
        
                                                # because of threading make sure no thread
                                                # changes value until we get them
                                                # and reset them
                                                

# start main demo function
main()

