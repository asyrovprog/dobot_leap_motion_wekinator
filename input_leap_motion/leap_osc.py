from OSC import OSCClient, OSCMessage, OSCError
SEND_NAMES = False

# https://github.com/hughrawlinson/wekinator-node
class osc_sender_t:
    def __init__(self, server, port):
        self.client = OSCClient()
        self.client.connect((server, port))
        self.need_send_names = SEND_NAMES

    def send_data(self, data):
        msg = OSCMessage("/wek/inputs")
        for k, v in data.items():
            if k.endswith("_flag"):
                msg.append(v)
            else:
                msg.append([v[0], v[1], v[2]])
        self._send(msg)

    def send_DTW_record(self, cls):
        msg = OSCMessage("/wekinator/control/startDtwRecording")
        msg.append(int(cls))
        self._send(msg)

    def send_DTW_stop(self):
        msg = OSCMessage("/wekinator/control/stopDtwRecording")
        self._send(msg)

    def send_run(self):
        msg = OSCMessage("/wekinator/control/startRunning")
        self._send(msg)

    def send_stop(self):
        msg = OSCMessage("/wekinator/control/stopRunning")
        self._send(msg)

    def send_names(self, data):
        if self.need_send_names:
            self.need_send_names = False
            msg = OSCMessage("/wekinator/control/setInputNames")
            for k, v in data.items():
                if k.endswith("flag"):
                    msg.append(k)
                else:
                    msg.append(k + "_x")
                    msg.append(k + "_y")
                    msg.append(k + "_z")
            self._send(msg)

    def _send(self, msg):
        try:
            self.client.send(msg)
        except OSCError:
            pass