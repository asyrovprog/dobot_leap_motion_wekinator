from ctypes import *
import dobot_api as dType
from pythonosc import dispatcher
from pythonosc import osc_server
import asyncio

CON_STR = { dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
            dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
            dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

SERVER_IP        = "127.0.0.1"
SERVER_PORT      = 12000
SERVER_PORT_POS  = 12001

api         = None
lastIndex   = -1
server      = None
dragging    = False

def explain(path, args = ""):
    print(path + "" + str(args))

def wek_dobot_drag_start(path):
    global dragging
    explain(path)
    dType.SetQueuedCmdClear(api)
    dragging = True

def wek_dobot_drag_stop(path):
    global dragging
    explain(path)
    dType.SetQueuedCmdClear(api)
    dragging = False

def dobot_gripper_open(path, args):
    explain(path, args)
    global  lastIndex
    dType.SetQueuedCmdClear(api)
    lastIndex = dType.SetEndEffectorGripper(api, 1, 0, isQueued = 1)[0]
    lastIndex = dType.SetWAITCmd(api, 0.5, isQueued = 1)[0]
    lastIndex = dType.SetEndEffectorGripper(api, 0, 0, isQueued = 1)[0]

def clear_alarm(path, args):
    explain(path, args)
    dType.ClearAllAlarmsState(api)

def weki_outputs(path, a, b, c):
    explain(path, (a, b, c))

def wek_dobot_gripper_open(path):
    dobot_gripper_open(path, 0)

def wek_dobot_gripper_close(path):
    dobot_gripper_close(path, 0)

def weki_dobot_home(path):
    dobot_home(path, 0)

def dobot_gripper_off(path, args):
    explain(path, args)
    global lastIndex
    lastIndex = dType.SetEndEffectorGripper(api, 0, 0, isQueued = 0)[0]

def dobot_gripper_close(path, args):
    explain(path, args)
    global lastIndex
    dType.SetQueuedCmdClear(api)
    lastIndex = dType.SetEndEffectorGripper(api, 1, 1, isQueued = 1)[0]
    lastIndex = dType.SetWAITCmd(api, 0.5, isQueued = 1)[0]
    lastIndex = dType.SetEndEffectorGripper(api, 0, 0, isQueued = 1)[0]

def dobot_shutdown(path, args):
    explain(path, args)
    server.shutdown()

def dobot_home(path, args):
    explain(path, args)
    dType.SetHOMEParams(api, 250, 0, 50, 0, isQueued = 1)
    dType.SetHOMECmd(api, temp = 0, isQueued = 1)

def dobot_status(path, args):
    explain(path, args)
    pose = dType.GetPose(api)
    print("\nCurrent pose:")
    print("Pose coordinates:")
    print("x, y, z, rHead:", pose[0], pose[1], pose[2], pose[3])
    print("Pose joints:")
    print("J1, J2, J3, J4:", pose[4], pose[5], pose[6], pose[7])

def weki_dobot_position(path, x, y, z):
    global lastIndex
    if dragging:
        x, y, z, r = round(float(x)), round(float(y)), round(float(z)), 0.0
        explain(path, (x, y, z))
        mode = dType.PTPMode.PTPMOVJXYZMode
        dType.SetQueuedCmdClear(api)
        lastIndex = dType.SetPTPCmd(api, mode, x, y, z, r, isQueued = 1)[0]

def dobot_ptp(path, ptp_type, x, y, z, r):
    global lastIndex
    x, y, z, r = float(x), float(y), float(z), float(r)
    explain(path, (ptp_type, x, y, z, r))

    mode = None
    if ptp_type == "jump_xyz":
        mode = dType.PTPMode.PTPJUMPXYZMode
    elif ptp_type == "movj_xyz":
        mode = dType.PTPMode.PTPMOVJXYZMode
    elif ptp_type == "movl_xyz":
        mode = dType.PTPMode.PTPMOVLXYZMode
    elif ptp_type == "jump_angle":
        mode = dType.PTPMode.PTPJUMPANGLEMode
    elif ptp_type == "movj_angle":
        mode = dType.PTPMode.PTPMOVJANGLEMode
    elif ptp_type == "movl_angle":
        mode = dType.PTPMode.PTPMOVLANGLEMode
    elif ptp_type == "movj_inc":
        mode = dType.PTPMode.PTPMOVJANGLEINCMode
    elif ptp_type == "movl_inc":
        mode = dType.PTPMode.PTPMOVLXYZINCMode
    elif ptp_type == "movj_xyz_inc":
        mode = dType.PTPMode.PTPMOVJXYZINCMode
    else:
        print("Unexpected mode: " + ptp_type)

    if mode is not None:
       lastIndex = dType.SetPTPCmd(api, mode, x, y, z, r, isQueued = 1)[0]

def main():
    global api, lastIndex, server

    api = cdll.LoadLibrary("libDobotDll.so")
    lastIndex = -1
    state = dType.ConnectDobot(api, "", 115200)[0]

    if state == dType.DobotConnect.DobotConnect_NoError:

        dp = dispatcher.Dispatcher()
        dp.map("/dobot/gripper/open", dobot_gripper_open)
        dp.map("/dobot/gripper/close", dobot_gripper_close)
        dp.map("/dobot/gripper/off", dobot_gripper_off)
        dp.map("/dobot/shutdown", dobot_shutdown)
        dp.map("/dobot/home", dobot_home)
        dp.map("/dobot/status", dobot_status)
        dp.map("/dobot/ptp", dobot_ptp)
        dp.map("/dobot/alarm/clear", clear_alarm)

        # These are for wekinator HandGestures project
        dp.map("/wek/dobot/drag", wek_dobot_drag_start)
        dp.map("/wek/dobot/stop", wek_dobot_drag_stop)
        dp.map("/wek/dobot/open", wek_dobot_gripper_open)
        dp.map("/wek/dobot/close", wek_dobot_gripper_close)

        # For wekinator HandMapping project
        dp1 = dispatcher.Dispatcher()
        dp1.map("/wek/dobot/pos", weki_dobot_position)


        # Clean Command Queued
        dType.SetCmdTimeout(api, 1000)
        dType.ClearAllAlarmsState(api)
        dType.SetQueuedCmdClear(api)
        dType.SetQueuedCmdStopExec(api)
        dType.SetQueuedCmdStartExec(api)

        loop = asyncio.get_event_loop()
        server = osc_server.AsyncIOOSCUDPServer((SERVER_IP, SERVER_PORT), dp, loop)
        server1 = osc_server.AsyncIOOSCUDPServer((SERVER_IP, SERVER_PORT_POS), dp1, loop)

        print("\033[2J\033[H")
        print("---------------------------------------------------------")
        print("                 Dobot OSC controller\n")
        print("       Waiting gestures on", SERVER_IP, SERVER_PORT)
        print("      Waiting positions on", SERVER_IP, SERVER_PORT_POS)
        print("---------------------------------------------------------")

        server.serve()
        server1.serve()
        loop.run_forever()

        # Stop to Execute Command Queued
        dType.SetQueuedCmdStopExec(api)

        # Disconnect Dobot
        dType.DisconnectDobot(api)
    else:
        print("\nFailed connect to Dobot: " + CON_STR[state])
        print("May need to run:\nsudo chmod 777 /dev/ttyUSB0")

if __name__ == "__main__":
    main()
