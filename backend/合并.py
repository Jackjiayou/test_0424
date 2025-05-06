from pydub import AudioSegment
import os
# 加载多个音频
audio1 = AudioSegment.from_wav(r"E:\work\code\test_uniapp\test_0424\backend\uploads\voice\介绍双迪标准.wav")
audio2 = AudioSegment.from_wav(r"E:\work\code\test_uniapp\test_0424\backend\uploads\voice\卡曼公司是双迪.wav")
audio3 = AudioSegment.from_wav(r"E:\work\code\test_uniapp\test_0424\backend\uploads\voice\今天天气怎么样标准的.wav")

# 合并音频（顺序拼接）
combined = audio1 + audio2 + audio3

# 导出为新文件
combined.export(r"E:\work\code\test_uniapp\test_0424\backend\uploads\combined\combined.wav", format="wav")




# 指定包含 .wav 文件的文件夹路径
folder_path = "./uploads/combined"  # 修改为你的实际路径

# 获取所有 .wav 文件（按文件名排序）
wav_files = sorted([
    f for f in os.listdir(folder_path)
    if f.lower().endswith(".wav")
])

# 合并音频
combined = AudioSegment.empty()
for filename in wav_files:
    file_path = os.path.join(folder_path, filename)
    audio = AudioSegment.from_wav(file_path)
    combined += audio
    print(f"已添加: {filename}")

# 导出合并后的音频
output_path = os.path.join(folder_path, "combined.wav")
combined.export(output_path, format="wav")
print(f"\n合并完成，输出文件: {output_path}")
