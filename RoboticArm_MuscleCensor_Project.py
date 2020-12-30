## ----------------------------------------------------------------------------------------------------------
## TEMPLATE
## Please DO NOT change the naming convention within this template. Some changes may
## lead to your program not functioning as intended.

import random
import sys
import time
sys.path.append('../')

from Common_Libraries.p2_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer

def update_sim ():
    try:
        arm.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

arm = qarm()

update_thread = repeating_timer(2, update_sim)


## STUDENT CODE BEGINS
## ----------------------------------------------------------------------------------------------------------
## Example to rotate the base: arm.rotateBase(90)

#blue =90, red = 158, green = -90

'''
This function returns the location(x,y,z) coordinates of where we want the q-arm
to move to. Includes all drop off location as well as the pickup location. Only
"bug" is that the small container drop off locations sometimes don't match up,
resulting in the containers sometimes not fitting- while other run throughs they
fit perfectly. Returns a list of the x, y, z coordinates when called.
'''
def autoclave_location(container_ID):
    location=[]
    #pickup location
    if container_ID==0:
        location=[0.5088, 0.0044, 0.0404]
    #red & small location
    elif container_ID==1:
        location=[-0.5809, 0.2306, 0.393]
    #green & small location
    elif container_ID==2:
        location=[0.0, -0.6529, 0.4041]
    #blue & small location
    elif container_ID==3:
        location=[0.0, 0.6529, 0.4041]
    #red & large location
    elif container_ID==4:
        location=[-0.4052, 0.1636, 0.1954]
    #green & large location
    elif container_ID==5:
        location =[0.0, -0.437, 0.1696]
    #blue & large location
    elif container_ID==6:
        location= [0.0, 0.437, 0.1696]
    #returns a list of the x, y, z coordinates
    return location


'''
This function controls the opening/closing of the autoclave bin drawers.
It is set up so that the left arm must be over a certain threshold and the
right arm must be between 2 set thresholds. The best way to do this would be to
set the right arm just above the minimum red/green/blue thresholds, and then set
the left to the same interval. Only after opening do we place the container
into the autoclave drawer. 
'''
def control_autoclave_bin_drawer():
   
    red_Thresh=0.2
    green_Thresh=0.4
    blue_Thresh=0.6
    # only opens the blue drawer given the conditions are true
    # Left Arm > 0.6, Right arm is between 0.6 and 0.9
    if arm.emg_left()>blue_Thresh and arm.emg_right()<0.9 and arm.emg_right()>blue_Thresh:
        arm.open_blue_autoclave(True)
        arm.open_green_autoclave(False)
        arm.open_red_autoclave(False)
    #only opens the green drawer given the conditions are true
    # Left Arm >0.4, Right arm is between 0.4 and 0.6
    elif arm.emg_left()>green_Thresh and arm.emg_right()<blue_Thresh and arm.emg_right()>green_Thresh:
        arm.open_green_autoclave(True)
        arm.open_blue_autoclave(False)
        arm.open_red_autoclave(False)
    #only opens the red drawer given the conditions are true
    # Left Arm >0.2, Right arm is between 0.2 and 0.4
    elif arm.emg_left() > red_Thresh and arm.emg_right()<green_Thresh and arm.emg_right()>red_Thresh:
        arm.open_red_autoclave(True)
        arm.open_blue_autoclave(False)
        arm.open_green_autoclave(False)
    # if none of the conditions are met, all drawers are kept closed
    else:
        arm.open_blue_autoclave(False)
        arm.open_green_autoclave(False)
        arm.open_red_autoclave(False)

'''
The longest/most complicated function of the entire program. This function
controls the arm movement given thresholds. This function runs through a series of
thresholds (from largest-> smallest) and controls the q-arm using both arms. 


Firstly, we can control the arm movement between the home position (0.00-0.05 &
0.1-0.2) and the pickup position (0.05-0.1) to allow for smoother movements
for the q-arm.

To move to the desired autoclave, we control the Q-arm by setting both 
arms to the q-rotate interval wanted. This will rotate the q-arm to the desired
autoclave and also open the drawer if we need to place a large container inside.
From there, we simply match the arm sensors for the desired dropoff location
(using the right arm first, then the left arm to prevent clipping).
'''
def  move_end_effector():

    #home/pickup location thresholds
    pickup_Thresh= 0.05
    home_thresh=0.1
    #thresholds for red containers
    red_rotate=0.2
    red_small= 0.25
    red_large=0.3
    #thresholds for green containers
    green_rotate= 0.4
    green_small= 0.45
    green_large=0.5
    #thresholds for blue containers
    blue_rotate=0.6
    blue_small=0.65
    blue_large=0.7

    # turn movements before arm movement( to prevent clipping the arm into the autoclaves)
    red_turn = [-0.3768, 0.1522, 0.4826]
    green_turn = [0.0, -0.4064, 0.4826]
    blue_turn = [0.0, 0.4064, 0.4826]

    home_position= [0.4064, 0.0, 0.4826]

    time.sleep(0.25)

    #locations for blue containers
    if arm.emg_left()> blue_rotate and arm.emg_right()>blue_rotate:
        #move to location for blue & large drop off
        if arm.emg_right() >blue_large and arm.emg_left()>blue_large:
            loc= autoclave_location(6)
            arm.move_arm(loc[0],loc[1], loc[2])
        #loication for blue & small drop off
        elif arm.emg_right()> blue_small and arm.emg_right()<blue_large and arm.emg_left()>blue_small:
            loc= autoclave_location(3)
            arm.move_arm(loc[0],loc[1], loc[2])
        #else - move to turn location for blue containers
        else:
            arm.move_arm(blue_turn[0],blue_turn[1], blue_turn[2])

    #locations for green containers
    elif arm.emg_left()>green_rotate and arm.emg_right()>green_rotate and arm.emg_right()<blue_rotate:
        #move to location for green & large drop off
        if arm.emg_right()>green_large and arm.emg_left()>green_large:
            loc= autoclave_location(5)
            arm.move_arm(loc[0],loc[1], loc[2])
        #move to location for green & small drop off
        elif arm.emg_right()> green_small and arm.emg_right()<green_large and arm.emg_left()> green_small:
            loc= autoclave_location(2)
            arm.move_arm(loc[0],loc[1], loc[2])
         #else - move to turn location for green containers
        else: 
            arm.move_arm(green_turn[0],green_turn[1], green_turn[2])

    #locations for red containers
    elif arm.emg_left()>red_rotate and arm.emg_right()>red_rotate and arm.emg_right()<green_rotate:
        #move to location for red & large drop off
        if arm.emg_right()>red_large and arm.emg_left()>red_large:
            loc= autoclave_location(4)
            arm.move_arm(loc[0],loc[1], loc[2])
        #move to location for red & small drop off
        elif arm.emg_right()> red_small and arm.emg_left()>red_small and arm.emg_right()<red_large:
            loc= autoclave_location(1)
            arm.move_arm(loc[0],loc[1], loc[2])
         #else - move to turn location for red containers
        else:
            arm.move_arm(red_turn[0],red_turn[1], red_turn[2])

    #moves to the home position if the right arm threshold is between 0.1 and 0.2
    elif arm.emg_right()>home_thresh:
        arm.move_arm(home_position[0], home_position[1], home_position[2])

    #moves to the pickup position if the right arm threshold is between 0.05 and 0.1
    elif arm.emg_right()>pickup_Thresh:
        loc = autoclave_location(0)
        arm.move_arm(loc[0],loc[1], loc[2])

    #back to home position when less than 0.05
    else:
        arm.home()
        
'''
Simply controls the gripper. If the threshold for the left arm is greater than 0.1, it closes the gripper
and if the threshold is greater than 0.9 it drops the container.
Returns a true/false boolean value that determines if the container is dropped to restart the process with
a new container.
'''
def control_Gripper():
    close_gripper = 0.1
    open_gripper = 0.9
    #opens gripper if the left arm threshold is greater than 0.9
    #also returns true - that the process for spawning the next container can be started
    if arm.emg_left() >open_gripper:
        time.sleep(0.5)
        arm.control_gripper(-45)
        return True
    #closes the gripper if the left threshold is greater than 0.1
    #returns false and we only pickup the container when this happens
    elif arm.emg_left()>close_gripper:
        arm.control_gripper(45)
        return False
    #else- do nothing with the gripper
    else:
        arm.control_gripper(0)
        return False
    
#main function
'''
Procedure:
1: Spawn container that hasn't been spawned before
2: Place arm in pickup position(Right muscle 0.05-0.1)
3: Grip Container(0.2>Left muscle >0.1)
4: Place arm in home position (0.1< right muscle<0.2)
5: Set right muscle to the turn position of the color of container (see thresholds above)
6: Set left muscle to the same threshold range.
7: After arm turns, set right muscle to threshold range of container location. Set left to the same. 
8: If location correct, set left muscle to > 0.9 to release container. If location WRONG, return right arm to home
threshold range and restart from step 4.
9: Set Left arm to zero to spawn the next container.
10: Repeat from step 2 until all 6 containers are placed in their respective autoclaves.
11: Once program finishes, all autoclaves should close and the q-arm should be in the home position. 
'''
def main():
    arm.home()
    time.sleep(0.5)
    home = [0.4064, 0.0, 0.4826]
    #list for determining when to finish the program, and inventory the containers placed 
    containers_spawned_list =[]
    #simply a counter to get out of the loop when the length is reached
    container_count=0
    while container_count <6:
        time.sleep(0.5)
        #this loop checks and determines a new container to spawn, depending on what has already been spawned
        # and added to the containers spawned list
        already_spawned=False
        while True:
            container_ID=random.randint(1,6)
            for i in containers_spawned_list:
                if i == container_ID:
                    already_spawned= True
                    break
                else:
                    already_spawned = False

            if already_spawned == False:
                containers_spawned_list.append(container_ID)
                arm.spawn_cage(container_ID)
                break
            time.sleep(1)

        # this loop runs all functions until the container is placed and control gripper returns true
        placed=False
        while True:
            time.sleep(0.5)
            control_autoclave_bin_drawer()
            move_end_effector()
            placed = control_Gripper()
            #will not exit the loop until the left arm is set to zero
            if placed == True:
                while (arm.emg_left()!= 0):
                    print("Please set the left arm to zero to continue the program. ")
                    control_autoclave_bin_drawer()
                    move_end_effector()
                    time.sleep(0.25)
                break
        time.sleep(0.2)
        container_count = len(containers_spawned_list)
        time.sleep(0.2)

    arm.home()
    time.sleep(0.25)
    control_autoclave_bin_drawer()
    time.sleep(0.25)
    print(" All Containers returned. Program finished. Thank you for trying our 1P13 P2 program! ")
    
    '''simply here to make sure that the drawers are closed- the program sometimes would exit too quickly and keep
    a drawer open'''
    
    

main()



