from gtts import gTTS
from pydub import AudioSegment, silence
import os
import random

output_dir = "synthetic_data"
os.makedirs(output_dir, exist_ok=True)

# 文本示例
sentences = [
    "I would like to share my thoughts on this topic.",
    "Speaking English fluently requires a lot of practice.",
    "Sometimes I struggle to find the right words.",
    "The weather today is really nice for a walk.",
    "This is an important subject for many students."
]

def add_pause(audio, num_pauses=1):
    """在音频中插入静音模拟停顿"""
    pause = AudioSegment.silent(duration=400)  # 400ms 停顿
    for _ in range(num_pauses):
        pos = random.randint(500, len(audio) - 500)
        audio = audio[:pos] + pause + audio[pos:]
    return audio

def save_sample(text, score, sample_id, fluency_level):
    tts = gTTS(text)
    tts.save("temp.mp3")
    audio = AudioSegment.from_mp3("temp.mp3")

    # 不同流利度处理
    if fluency_level == "mid":
        audio = add_pause(audio, num_pauses=1)
    elif fluency_level == "low":
        text = text.replace(",", " uh,").replace("and", "um and")
        tts = gTTS(text)
        tts.save("temp.mp3")
        audio = AudioSegment.from_mp3("temp.mp3")
        audio = add_pause(audio, num_pauses=3)

    filename = f"sample_{sample_id}_{fluency_level}.wav"
    audio.export(os.path.join(output_dir, filename), format="wav")
    return filename

# 标签保存
labels = {}

sample_id = 1
for fluency_level, score_range in [("high", (4.5, 5.0)), ("mid", (3.0, 4.0)), ("low", (1.0, 2.5))]:
    for text in sentences:
        score = round(random.uniform(*score_range), 2)
        fname = save_sample(text, score, sample_id, fluency_level)
        labels[fname] = score
        sample_id += 1

# 保存标签为 CSV（可选）
import csv
with open(os.path.join(output_dir, "labels.csv"), "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["filename", "score"])
    for k, v in labels.items():
        writer.writerow([k, v])

print("✅ 合成语音生成完毕，路径：", output_dir)
