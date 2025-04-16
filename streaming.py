# streaming.py
# Video/audio capturing and sending via WebRTC

from aiortc import VideoStreamTrack, AudioStreamTrack
import numpy as np
import mss
import pyaudio

class ScreenTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.sct = mss.mss()
        monitor = self.sct.monitors[1]
        self.region = {'top': monitor['top'], 'left': monitor['left'], 'width': monitor['width'], 'height': monitor['height']}

    async def recv(self):
        frame = await super().recv()
        img = np.array(self.sct.grab(self.region))
        return frame

class AudioTrack(AudioStreamTrack):
    def __init__(self):
        super().__init__()
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=pyaudio.paInt16, channels=2, rate=48000, input=True, frames_per_buffer=1024)

    async def recv(self):
        data = self.stream.read(1024)
        return data
