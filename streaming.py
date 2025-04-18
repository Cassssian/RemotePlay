# streaming.py
# Video/audio capturing and sending via WebRTC

from aiortc import VideoStreamTrack, AudioStreamTrack
from av import VideoFrame
from aiortc.mediastreams import AudioFrame
import numpy as np
import mss
import cv2
import sounddevice as sd

class ScreenTrack(VideoStreamTrack):
    """
    Capture l'écran et le transmet en tant que flux vidéo.
    """
    def __init__(self):
        super().__init__()
        self.sct = mss.mss()  # Utilisation de mss pour capturer l'écran
        monitor = self.sct.monitors[1]  # Capture le premier écran
        self.region = {
            "top": monitor["top"],
            "left": monitor["left"],
            "width": monitor["width"],
            "height": monitor["height"]
        }

    async def recv(self):
        """
        Capture une image de l'écran et la transmet sous forme de frame vidéo.
        """
        # Capture l'écran
        img = np.array(self.sct.grab(self.region))

        # Convertir l'image en format BGR pour OpenCV
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Créer une frame vidéo avec PyAV
        frame = VideoFrame.from_ndarray(img, format="bgr24")
        frame.pts, frame.time_base = await self.next_timestamp()
        return frame

class AudioTrack(AudioStreamTrack):
    """
    Capture l'audio du microphone et le transmet en tant que flux audio.
    """
    def __init__(self):
        super().__init__()
        self.sample_rate = 48000
        self.channels = 2
        self.stream = sd.InputStream(samplerate=self.sample_rate, channels=self.channels, dtype="int16")
        self.stream.start()

    async def recv(self):
        audio_data, _ = self.stream.read(1024)
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        frame = AudioFrame.from_ndarray(audio_array, format="s16", layout="stereo")
        frame.pts, frame.time_base = await self.next_timestamp()
        return frame
