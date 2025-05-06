import requests

# Flask 服务器地址
url = "http://127.0.0.1:5000/score"

# 本地测试音频路径（改成你本地的音频文件路径）
#audio_path = r"E:\work\code\test_uniapp\test_0424\backend\uploads\voice\audio_1745998379439_2sn0fj_16k.wav"
audio_path = r"E:\work\code\test_uniapp\test_0424\backend\uploads\tts\1745981119.mp3"

# POST 请求，上传音频
with open(audio_path, 'rb') as f:
    files = {'audio': f}
    response = requests.post(url, files=files)

# 打印响应结果
if response.ok:
    print("结果：", response.json())
else:
    print("请求失败：", response.status_code, response.text)
