import requests

# API 地址
url = "http://117.50.91.160:8000//process/"

# 准备文件
files = {
    'video_file': ('input.mp4', open(r'E:\work\虚拟人\hr.mp4', 'rb'), 'video/mp4'),
    'audio_file': ('input.wav', open(r'E:\work\虚拟人\1747033032.mp3', 'rb'), 'audio/mp3')
}

# 可选参数
params = {
    'inference_steps': 20,  # 可选，默认值为20
    'guidance_scale': 2.0   # 可选，默认值为2.0
}

# 发送请求
response = requests.post(url, files=files, data=params)

# 保存处理后的视频
if response.status_code == 200:
    with open('output.mp4', 'wb') as f:
        f.write(response.content)
    print("视频处理成功，已保存为 output.mp4")
else:
    print(f"处理失败: {response.text}")