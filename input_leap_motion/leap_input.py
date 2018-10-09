import Leap
from leap_osc import *
from leap_canvas import *

WEKINATOR_SERVER = "localhost"
PORT_HAND        = 6447
PORT_GESTURE     = 6448


class SampleListener(Leap.Listener):
    finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
    bone_names   = ['metacarpal', 'proximal', 'intermediate', 'distal']

    def __init__(self):
        super(SampleListener, self).__init__()
        self.frame = {}
        self.init_frame()
        self.ibox = None
        self.osc_hand = osc_sender_t(WEKINATOR_SERVER, PORT_HAND)
        self.osc_gest = osc_sender_t(WEKINATOR_SERVER, PORT_GESTURE)
        self.visualizer = None
        self.init_frame()
        self.gesture_id = "0"
        self.send_gesture = False
        self.training_gesture = False
        self.send_hand = False
        self.id = 0

    def send_box_point(self, char):
        points = {"a": (0.0, 0.0, 0.0), "b": (0.0, 0.0, 1.0), "c": (0.0, 1.0, 1.0), "d": (0.0, 1.0, 0.0),
                  "e": (1.0, 0.0, 0.0), "f": (1.0, 0.0, 1.0), "g": (1.0, 1.0, 1.0), "h": (1.0, 1.0, 0.0)}
        point = points[str(char)]
        self.osc_gest.send_data({"hand": point})

    def toggle_DTW(self, char):
        if self.send_gesture:
            self.toggle_gesture()

        if self.training_gesture:
            self.osc_gest.send_DTW_stop()
            self.training_gesture = False
            self.gesture_id = "0"
        else:
            self.osc_gest.send_DTW_record(str(char))
            self.gesture_id = str(char)
            self.training_gesture = True

    def toggle_gesture(self):
        if self.training_gesture:
            self.toggle_DTW()

        self.send_gesture = not self.send_gesture
        if self.send_gesture:
            self.osc_gest.send_run()
        else:
            self.osc_gest.send_stop()

    def toggle_positions(self):
        self.send_hand = not self.send_hand
        if self.send_hand:
            self.osc_hand.send_run()
        else:
            self.osc_hand.send_stop()

    def clear_hand_data(self):
        f = self.frame
        f["hand_flag"] = 0.0
        f["hand"]      = (0.0, 0.0, 0.0)
        for fn in self.finger_names:
            i = 0
            for b in self.bone_names:
                name = fn + "_" + b
                if i == 0:
                    f[name + "_prev"] = (0.0, 0.0, 0.0)
                f[name + "_next"]     = (0.0, 0.0, 0.0)
                i += 1

    def init_frame(self):
        self.clear_hand_data()

    def render_frame(self):
        if self.frame["hand_flag"] == 0:
            return
        origin = self.frame["hand"]
        for k, v in self.frame.items():
            if self.visualizer is not None:
                self.visualizer.set_point(k, v, origin)

        # for OSC hand, we send only hand position

        if self.send_hand:
            if self.id % 20 == 0:
                self.osc_hand.send_data({"hand": origin})
            self.id += 1

        # for OSC gesture, we send locations of bones, but not
        # hand position, because gesture is independent of it
        if self.send_gesture or self.training_gesture:
            del self.frame["hand"]
            self.osc_gest.send_data(self.frame)
            self.frame["hand"] = origin

    def norm(self, pos):
        if self.ibox is not None:
            return self.ibox.normalize_point(pos, clamp = False)
        return pos

    def add(self, name, value):
        if not name in self.frame:
            raise LookupError
        self.frame[name] = value

    def on_frame(self, controller):
        frame = controller.frame()
        self.init_frame()
        self.ibox = frame.interaction_box

        for hand in frame.hands:
            if not hand.is_left:
                continue
            palm = self.norm(hand.palm_position)
            self.add("hand_flag", 1.0)
            self.add("hand", palm)
            for finger in hand.fingers:
                finger_name = self.finger_names[finger.type]
                for b in range(0, 4):
                    bone = finger.bone(b)
                    bone_name = self.bone_names[bone.type]
                    name = finger_name + "_" + bone_name
                    if b == 0:
                        self.add(name + "_prev", self.norm(bone.prev_joint) - palm)
                    self.add(name + "_next", self.norm(bone.next_joint) - palm)

        self.render_frame()

def main():
    listener = SampleListener()
    controller = Leap.Controller()
    controller.add_listener(listener)

    Paint(listener)
    controller.remove_listener(listener)

if __name__ == "__main__":
    main()
