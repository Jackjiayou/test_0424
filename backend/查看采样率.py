import subprocess
import librosa
import soundfile as sf

from pydub.utils import which
from pydub import AudioSegment


# audio_path = './1.mp3'
# audio_path = './3.mp3'
# audio_path = './nls-sample-16k.wav'

#signal, sr = librosa.load(audio_path, sr=None)
# # sr=None 表示保留原始采样率[^2]
# print("采样率:", sr) # 输出如 44100
# print('shape:'+str(signal.dtype.itemsize * 8))
# y, sr = librosa.load(audio_path, sr=None)
# length_in_seconds = librosa.get_duration(y=y, sr=sr)
# print(f"音频长度为: {length_in_seconds} 秒")

if __name__ == "__main__":
    #audio_path1 = r".\uploads\tts\1745893171.mp3"
    audio_path = r'E:\work\code\test_uniapp\test_0424\backend\uploads\voice\问题0508\audio_1746676895529_4u33xs_16k.mp3'
    signal, sr = librosa.load(audio_path, sr=None)


    # 打印采样率
    print(f"采样率: {sr} Hz")

