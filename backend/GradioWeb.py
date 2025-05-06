import gradio as gr
import librosa
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor

# ====== 提取音频流利度特征函数 ======
def extract_fluency_features(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    hop_length = 512
    frame_length = 2048

    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_delta = librosa.feature.delta(mfccs)
    mfcc_delta_std = np.std(mfcc_delta)

    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    avg_rms = np.mean(rms)
    num_pauses = np.sum(rms < 0.02)

    zcr = librosa.feature.zero_crossing_rate(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    avg_zcr = np.mean(zcr)

    duration = librosa.get_duration(y=y, sr=sr)
    voiced_ratio = np.sum(rms > 0.02) * hop_length / sr / duration
    speech_rate_estimate = voiced_ratio / duration

    return [
        mfcc_delta_std, avg_rms, num_pauses,
        avg_zcr, voiced_ratio, speech_rate_estimate, duration
    ]

# ====== 加载训练好的模型（你可先保存模型） ======
# 假设你已经用之前训练好的模型保存成了 model.pkl
# 如果没有，可以在脚本末尾加上保存模型代码：
# with open("model.pkl", "wb") as f:
#     pickle.dump(model, f)

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# ====== 预测函数供 Gradio 使用 ======
def predict_fluency(audio_file):
    try:
        features = extract_fluency_features(audio_file)
        score = model.predict([features])[0]
        return f"🌟 预测流利度得分：{score:.2f} / 5.0"
    except Exception as e:
        return f"❌ 分析失败：{e}"

# ====== Gradio 界面搭建 ======
gr.Interface(
    fn=predict_fluency,
    inputs=gr.Audio(type="filepath", label="上传一段说话的音频 (.wav)"),
    outputs="text",
    title="🎤 音频流利度评估系统",
    description="上传一段说话音频，系统将评估说话的流利度（0–5分）",
    theme="soft"
).launch()

#
# import pickle
# with open("model.pkl", "wb") as f:
#     pickle.dump(model, f)
