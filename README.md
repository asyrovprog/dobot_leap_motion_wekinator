# Dobot Robot controlled by a hand in air using machine learning and Leap Motion

## Brief

   This is a simple  "space hand" (as I call it) controller for 
Dobot Robot. It gethers input (hand pose) from LeapMotion, then
recognizes  gestures/positions  and  process them using Machine
Learning  algorithms  (with  use of   Wekinator software), then
translates Wekinator  output OSC message to the robot API calls.

   Though LeapMotion provides some gesture recognition, it is  
not used, but instead machine learning algorithms are used to
do so.

## Video

https://www.youtube.com/watch?v=3WdiG9et4-w

## Structure:

Here is the description for most important files:
```
├── input_leap_motion                Forder for Leap Motion Input
│   ├── leap_input.py                Main program go gether input from Leap Motion
│   ├── leap_canvas.py                Utility code to display Position of left arm
│   └── leap_osc.py                   Utility OSC messaging
├--─ wekinator_projects               Folder for Wekinator Projects (ML)
│   ├── HandGestures                 Hand position (Linear Regression)
│   └── HandMapping                  Gesture recognition (Dynamic Time Warping)
└── output_dobot                     Dobot robot code
     ├── dobot_osc_controller         Dobot Output (reciever of Wekinator messages)  
     │   ├── dobot_api.py             Utility: python API for Dobot
     │   ├── dobot_osc_cmd.py         Utility: sort of command line to test commands
     │   └── dobot_osc_server.py     Main program that controls robot 
     └── official_sdk
```

## Installation:

   Dobot and LeapMotion are already running on your machine.
I used Arch  Linux  to  run  all of  the above programs, and while 
Python and Dobot SDK, and Leap Motion SKD are platform independent, 
the code will not run without minor  changes,  which  you  need to 
discover on your own (sorry for inconvinience)

   Leap Motion installed  using pacaur  and  then service started 
as described here: 

   https://github.com/sthysel/leapmotion

   After starting Leap Motion service run Visualizer executable
to make sure Leap Motion is operational.

   Input capture  application is written in  python 2. This is 
due to Leap Motion SDK at the moment only works with version 2.

   Quick overview of Leap Motion SDK:

   https://developer-archive.leapmotion.com/documentation/python/devguide/Leap_Overview.html

   UI part created with Tkinter library, some references are 
here:

   https://github.com/ChuntaoLu/PainT/blob/master/paint.py
   http://home.wlu.edu/~lambertk/breezypythongui/graphics.html

   Output device is Dobot robot. After installing SDK I rebuild 
API (DobotDll.pro) and copied all output files into my /usr/lib
  
   In order for robot to work using usb cable I run lsusb command
to check if QuinHeng... device is here and then run 

   `sudo chmod 777 /dev/ttyUSB0`
   
   There are 2 wekinator projects, one is to control postion of 
robot another is to recognize 4 gestures (drag, stop, open gripper,
close gripper). Wekinator is installed from http://www.wekinator.org
   




   
  
