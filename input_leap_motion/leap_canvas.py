from Tkinter import *
from pyrr import Matrix44, Vector4, Vector3
import tkMessageBox

Mat4 = Matrix44

WINDOW_SIZE = 800
POINT_SIZE  = 5
PALM_SIZE   = 10
PROJECTION  = 2.5
BACKGROUND  = "black"
STROKE      = ["green", "orange", "red"]

tk = None

class Paint(object):
    def __init__(self, parent = None):
        self.SIZE = WINDOW_SIZE
        self.root = Tk()
        self.canvas = Canvas(self.root, bg = BACKGROUND, width = self.SIZE, height = self.SIZE)
        self.canvas.pack()
        self.items = {}
        self.lm_input = None

        self.model_matrix = Mat4.from_scale([2, 2, 2]) * Mat4.from_translation([-0.5, -0.5, -0.5])
        self.view_matrix = Mat4.look_at((0, 0, 2.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))
        f = PROJECTION
        self.projection_matrix = Mat4.orthogonal_projection(-f, f, f, -f, f, -f)

        self.setup(parent)
        self.root.mainloop()
        self.root.quit()

        del self.root

    def setup(self, parent):
        self.lm_input = parent
        if parent is not None:
            parent.visualizer = self
        def ask_quit():
            parent.visualizer = None
            if tkMessageBox.askokcancel("Quit", "You want to quit the application now?"):
                self.root.destroy()
            else:
                parent.visualizer = self
        self.root.protocol("WM_DELETE_WINDOW", ask_quit)

        self.items["lastkey"] = self.canvas.create_text(10, 10,
                                                        text="Press a..h to send points of interation box",
                                                        anchor=W,
                                                        justify=LEFT,
                                                        fill="white")

        self.items["status_gesture"] = self.canvas.create_text(10, 30,
            text    = self.get_gesture_status(),
            fill    = "white",
            anchor  = W,
            justify = LEFT)

        self.items["status_position"] = self.canvas.create_text(10, 50,
                                                               text=self.get_position_status(),
                                                               fill="white",
                                                               anchor=W,
                                                               justify=LEFT)


        def down(e):
            if self.lm_input is not None:
                if e.char in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
                    self.lm_input.send_box_point(e.char)
                elif e.char == 'q':
                    self.lm_input.toggle_positions()
                elif e.char == 'p':
                    self.lm_input.toggle_gesture()
                elif e.char in ['1', '2', '3', '4', '5']:
                    self.lm_input.toggle_DTW(e.char)
                self.canvas.itemconfigure(self.items["status_gesture"],  text = self.get_gesture_status())
                self.canvas.itemconfigure(self.items["status_position"], text=self.get_position_status())

        self.root.bind('<KeyPress>', down)

    def get_gesture_status(self):
        li = self.lm_input
        if li.training_gesture:
            return "Training gesture " + li.gesture_id + ". Press any numeric key to stop."
        elif li.send_gesture:
            return "Running gesture recognition. Press 'p' to stop."
        else:
            return "Press 'p' to start gesture recognition or 1..5 to train."

    def get_position_status(self):
        li = self.lm_input
        if li.send_hand:
            return "Sending hand position. Press 'q' to stop."
        else:
            return "Press 'q' to start sending hand position."

    def to_screen(self, v_ndc):
        h = w = self.SIZE
        x = y = 0; n = -1; f = 1
        return Vector3([(v_ndc.x + 1) * (h/2) + x, (v_ndc.y + 1) * (w/2) + y, ((f - n)/2) * v_ndc.z + (f + n)/2])

    def mvps(self, pos):
        v_mod  = self.model_matrix * Vector4([pos[0], pos[1], pos[2], 1.])
        v_eye  = self.view_matrix * v_mod
        v_clip = self.projection_matrix * v_eye
        return self.to_screen(Vector3([v_clip.x, v_clip.y, v_clip.z]) / v_clip.w)

    def set_point(self, name, pos, offset):
        global STROKE
        size = POINT_SIZE
        if not name.endswith("_dir") and not name.endswith("flag") and not name.endswith("_normal"):
            if name != "hand":
                pos = Vector3([pos[0], pos[1], pos[2]]) + Vector3([offset[0], offset[1], offset[2]])
            else:
                size = PALM_SIZE
            x, y, z = self.mvps(pos)

            color_id = 0
            for i in range(3):
                if offset[i] > 1.1 or offset[i] < -0.1:
                    color_id = max(color_id, 2)
                elif offset[i] > 1 or offset[i] < 0:
                    color_id = max(color_id, 1)

            fill = STROKE[color_id]
            if name not in self.items:
                self.items[name] = self.canvas.create_oval(0, 0, POINT_SIZE, POINT_SIZE, fill = fill)
            self.canvas.coords(self.items[name], x, y, x + size, y + size)
            self.canvas.itemconfig(self.items[name], fill = fill)

    def paint(self, event):
        pass

    def clear_all(self):
        for i, ctrl in self.items():
            self.canvas.deleteItem(ctrl)
        self.items = {}

if __name__ == '__main__':
    Paint(None)