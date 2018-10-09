from pythonosc import udp_client

def handle_ptp(cmd, c):
    cmd = cmd.split(' ')
    if len(cmd) != 6 or cmd[1] not in ["jump_xyz", "movj_xyz", "movl_xyz",
                                       "jump_angle", "movj_angle", "movl_angle",
                                       "movj_inc", "movl_inc", "movj_xyz_inc"]:
        print("ERROR: Invalid command parameters")
        print("press <Enter> to continue...")
    else:
        for i in range(2, len(cmd)):
            cmd[i] = float(cmd[i])
        c.send_message("/dobot/ptp", cmd[1:])

def bounding_box(cmd, c):
    if cmd == "a":
        c.send_message("/dobot/ptp", ["movj_xyz", 150, -160, -30, 0])
    elif cmd == "b":
        c.send_message("/dobot/ptp", ["movj_xyz", 290, -140, -30, 0])
    elif cmd == "c":
        c.send_message("/dobot/ptp", ["movj_xyz", 290, -140, 90, 0])
    elif cmd == "d":
        c.send_message("/dobot/ptp", ["movj_xyz", 150, -160, 90, 0])
    elif cmd == "e":
        c.send_message("/dobot/ptp", ["movj_xyz", 150, 160, -30, 0])
    elif cmd == "f":
        c.send_message("/dobot/ptp", ["movj_xyz", 290, 140, -30, 0])
    elif cmd == "g":
        c.send_message("/dobot/ptp", ["movj_xyz", 290, 140, 90, 0])
    elif cmd == "h":
        c.send_message("/dobot/ptp", ["movj_xyz", 150, 160, 90, 0])

if __name__ == "__main__":

  client = udp_client.SimpleUDPClient("127.0.0.1", 12000)
  synopsis = "\033[2J\033[H" \
             "------------------------------------\n" \
             "     Dobot OSC command sender\n" \
             "------------------------------------\n" \
             "shutdown         - close apprication and server\n" \
             "home             - position to <home>\n" \
             "status           - status of the devide (pose, etc)\n" \
             "alarm/clear      - clear alarm flag (switch red to green)\n" \
             "gripper/open     - open gripper mouth\n" \
             "gripper/close    - close gripper mouth\n" \
             "gripper/off      - turn off gripper\n" \
             "a...h            - ptp jump to corners of bounding box\n" \
             "ptp              - point to point type, x, y, z, rotation\n" \
             "                       types: \n" \
             "                              jump_xyz     - jump mode to coordinates \n" \
             "                              movj_xyz     - joint move to coordinates \n" \
             "                              movl_xyz     - linear move to coordinates \n" \
             "                              jump_angle   - jump move to angular (joints from <status>)\n" \
             "                              movj_angle   - joint move to angular (joints from <status>)\n" \
             "                              movl_angle   - joint linear move to angular (joints from <status>)\n" \
             "                              movj_inc     - incremental joint move (joints from <status>)\n"\
             "                              movl_inc     - incremental linear move (joints from <status>)\n" \
             "                              movj_xyz_inc - incremental joint move (joints from <status>)\n" \
             "                       example: ptp jump_xyz 200 154 154 50\n" \
             "> "

  while True:
      r = input(synopsis)
      if r.startswith("ptp "):
          handle_ptp(r, client)
      elif len(r) == 1:
          bounding_box(r, client)
      else:
          client.send_message("/dobot/" + r, 0)

      if r == "shutdown":
          break
