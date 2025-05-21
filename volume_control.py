from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import ctypes
import re
from commands import COMMAND_MAP

class VolumeController:
    def __init__(self):
        self.volume_dll = ctypes.windll.LoadLibrary("winmm.dll")
        self.pycaw_volume = self._init_pycaw()
        self.triggers = COMMAND_MAP["volume"]["triggers"]
        self.presets = {
            'movie': 80, 'night': 30, 'normal': 50,
            'party': 100, 'quiet': 25, 'presentation': 65
        }
        self.word_to_level = {
            "max": 100, "full": 100,
            "half": 50, "quarter": 25,
            "mute": 0
        }

    def _init_pycaw(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_,
                CLSCTX_ALL,
                None)
            return cast(interface, POINTER(IAudioEndpointVolume))
        except Exception as e:
            print(f"[Init Error] Pycaw failed: {e}")
            return None

    def set_volume(self, level):
        try:
            # Convert named preset or string-based level
            if isinstance(level, str):
                level = self.presets.get(level, self.word_to_level.get(level.lower(), level))
                if isinstance(level, str) and level.startswith(("+", "-")):
                    level = int(level)
                    level = max(0, min(100, self.get_volume() + level))
                else:
                    level = int(level)

            level = max(0, min(100, level))  # Clamp to 0–100

            if self.pycaw_volume:
                self.pycaw_volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            else:
                self.volume_dll.waveOutSetVolume(0, level * 65535 // 100)

            return level
        except Exception as e:
            print(f"[Set Error] Volume setting failed: {e}")
            return None

    def get_volume(self):
        try:
            if self.pycaw_volume:
                return round(self.pycaw_volume.GetMasterVolumeLevelScalar() * 100)
            curr_vol = ctypes.c_uint()
            self.volume_dll.waveOutGetVolume(0, ctypes.byref(curr_vol))
            return (curr_vol.value & 0xFFFF) * 100 // 65535
        except:
            return 50

    def handle_command(self, transcript):
        transcript = transcript.lower()
        print(f"[Command Received] {transcript}")

        try:
            match = re.search(r'(\d{1,3})%?', transcript)
            if match:
                vol = self.set_volume(int(match.group(1)))
                return True, f"Volume set to {vol}%"

        # Keywords like "full", "half", etc.
            for word in self.word_to_level:
                if word in transcript:
                    vol = self.set_volume(word)
                    return True, f"Volume set to {vol}%"

        # Presets like "night mode", etc.
            for preset in self.presets:
                if preset in transcript:
                    vol = self.set_volume(preset)
                    return True, f"Volume set to {preset} mode ({vol}%)"

        # Mute / Unmute
            if "mute" in transcript:
                self.set_volume(0)
                return True, "Muted"
            if "unmute" in transcript:
                vol = self.set_volume(50)
                return True, f"Unmuted to {vol}%"

        # Volume adjustments
            if any(word in transcript for word in ["up", "increase", "louder","loud"]):
                vol = self.set_volume("+20")
                return True, f"Volume increased to {vol}%"
            if any(word in transcript for word in ["down", "decrease", "quieter", "lower", "fighter", "twitter", "quarter","quiet"]):
                vol = self.set_volume("-20")
                return True, f"Volume decreased to {vol}%"

        except Exception as e:
            print(f"[Command Error] {e}")

        return False, "Sorry, I didn't understand that volume command"

