from flask import Flask, request
import subprocess
import psutil

def terminate_process_by_name(script_name):
    found = False
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            # Check if 'server.py' is in the command line arguments
            if proc.info['cmdline'] and script_name in proc.info['cmdline']:
                found = True
                pid = proc.info['pid']
                print(f"Found process '{script_name}' with PID: {pid}. Terminating...")
                proc.terminate()
                proc.wait(timeout=5)  # Wait for the process to terminate
                print(f"Process '{script_name}' with PID: {pid} terminated.")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if not found:
        print(f"No process running '{script_name}' found.")


app = Flask(__name__)


initial = """

from picarx import Picarx
from pydoc import text
from vilib import Vilib

from time import sleep, time, strftime, localtime
import threading
import readchar
import os

px = Picarx()

gm_state = "none"

do_face= False
do_color = False

current_state = None
px_power = 10
offset = 20
last_state = "stop"

def outHandle():
    global last_state, current_state
    if last_state == 'left':
        px.set_dir_servo_angle(-30)
        px.backward(10)
    elif last_state == 'right':
        px.set_dir_servo_angle(30)
        px.backward(10)
    while True:
        gm_val_list = px.get_grayscale_data()
        gm_state = get_status(gm_val_list)
        currentSta = gm_state
        if currentSta != last_state:
            break
    sleep(0.001)

def get_status(val_list):
    _state = px.get_line_status(val_list)  # [bool, bool, bool], 0 means line, 1 means background
    if _state == [0, 0, 0]:
        return 'stop'
    elif _state[1] == 1:
        return 'forward'
    elif _state[0] == 1:
        return 'right'
    elif _state[2] == 1:
        return 'left'



#1
Color = "none"

#5
px.set_cliff_reference([1, 1,1])


#Car movement functions

def move_forward (distance = 1):

    px.forward(10)

    if distance != 100:

        sleep(1.08 * distance)


def move_backward (distance = 1):


    px.backward(10)

    if distance != 100:

        sleep(1.08 * distance)


def turn_left():

    px.set_dir_servo_angle(-20)


def turn_right():

    px.set_dir_servo_angle(20)


def center():

    px.set_dir_servo_angle(0)

def stop():
    px.stop()


def detect_color(param):
    
    global do_color
    
    do_color = True
    

    global Color

    Color = param

    Vilib.color_detect(param)


    if Vilib.detect_obj_parameter['color_n']!= 0: 
        return True 
    else:
        return False






def detect_face():
    
    global do_face
    do_face = True


    Vilib.face_detect_switch(True)


    if Vilib.detect_obj_parameter['human_n'] != 0:
        return True

    else:
        return False






def detect_obstacle():

    distance = round(px.ultrasonic.read(), 2)

    if distance < 30:
        return True
    else:
        return False



def detect_cliff():
    
    gm_val_list = px.get_grayscale_data()
    gm_state = px.get_cliff_status(gm_val_list)

    return gm_state


def detect_line():

    gm_val_list = px.get_grayscale_data()
    global gm_state
    gm_state = get_status(gm_val_list)




    
    


    
def followLine ():

    try:
            while True:
                gm_val_list = px.get_grayscale_data()
                gm_state = get_status(gm_val_list)
                print("gm_val_list: %s, %s"%(gm_val_list, gm_state))

                if gm_state != "stop":
                    last_state = gm_state

                if gm_state == 'forward':
                    px.set_dir_servo_angle(0)
                    px.forward(px_power)
                elif gm_state == 'left':
                    px.set_dir_servo_angle(offset)
                    px.forward(px_power)
                elif gm_state == 'right':
                    px.set_dir_servo_angle(-offset)
                    px.forward(px_power)
                else:
                    outHandle()
    finally:
            px.stop()
            sleep(0.1)


def followColor():
    
    global do_color
    
    if do_color == True:
    
        def clamp_number(num,a,b):
            return max(min(num, max(a, b)), min(a, b))
            
        global Color

        def main():
            
            global Color
        
            Vilib.color_detect(Color)
            speed = 50
            dir_angle=0
            x_angle =0
            y_angle =0
            while True:
                if Vilib.detect_obj_parameter['color_n']!=0:
                    coordinate_x = Vilib.detect_obj_parameter['color_x']
                    coordinate_y = Vilib.detect_obj_parameter['color_y']

                    # change the pan-tilt angle for track the object
                    x_angle +=(coordinate_x*10/640)-5
                    x_angle = clamp_number(x_angle,-35,35)
                    px.set_cam_pan_angle(x_angle)

                    y_angle -=(coordinate_y*10/480)-5
                    y_angle = clamp_number(y_angle,-35,35)
                    px.set_cam_tilt_angle(y_angle)

                    # move
                    # The movement direction will change slower than the pan/tilt direction
                    # change to avoid confusion when the picture changes at high speed.
                    if dir_angle > x_angle:
                        dir_angle -= 1
                    elif dir_angle < x_angle:
                        dir_angle += 1
                    px.set_dir_servo_angle(x_angle)
                    px.forward(speed)
                    sleep(0.05)

                else :
                
                    break
                    
        main()


def followCamera():
    
    global do_face
    
    if do_face == True:
        
        def clamp_number(num,a,b):
            return max(min(num, max(a, b)), min(a, b))

        x_angle =0
        y_angle =0

        try:
            while True:
                    if Vilib.detect_obj_parameter['human_n']!=0:
                        coordinate_x = Vilib.detect_obj_parameter['human_x']
                        coordinate_y = Vilib.detect_obj_parameter['human_y']

                        # change the pan-tilt angle for track the object
                        x_angle +=(coordinate_x*10/640)-5
                        x_angle = clamp_number(x_angle,-35,35)
                        px.set_cam_pan_angle(x_angle)

                        y_angle -=(coordinate_y*10/480)-5
                        y_angle = clamp_number(y_angle,-35,35)
                        px.set_cam_tilt_angle(y_angle)

                        sleep(0.05)

                    else :
                        
                        break
        finally:
            px.stop()
            sleep(0.1)  
       
       
Vilib.camera_start()
Vilib.display()     
       
       


"""


@app.route('/upload', methods=['POST'])
def upload_script():
    try:
        # Specify the process name
        process_name = 'picar_script.py'
        terminate_process_by_name(process_name)
        
        # Save the received script
        script = request.data.decode('utf-8')
        global initial
        with open('picar_script.py', 'w') as f:
            f.write(initial + script)
        # Optionally run the script automatically
        subprocess.run(['python3', 'picar_script.py'], check=True)
        return 'Script uploaded and executed', 200
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)


