import os
import numpy as np
import librosa
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error

# 音频特征提取函数
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

    return {
        'mfcc_delta_std': mfcc_delta_std,
        'avg_rms': avg_rms,
        'num_pauses': num_pauses,
        'avg_zcr': avg_zcr,
        'voiced_ratio': voiced_ratio,
        'speech_rate_estimate': speech_rate_estimate,
        'duration_sec': duration
    }

# 加载标签
data_dir = "synthetic_data"
df = pd.read_csv(os.path.join(data_dir, "labels.csv"))

# 提取所有样本的特征
X = []
y = []

for idx, row in df.iterrows():
    audio_path = os.path.join(data_dir, row['filename'])
    try:
        feats = extract_fluency_features(audio_path)
        X.append(list(feats.values()))
        y.append(row['score'])
    except Exception as e:
        print(f"Failed to process {audio_path}: {e}")

X = np.array(X)
y = np.array(y)

# 拆分训练/测试
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# 模型训练
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 评估
y_pred = model.predict(X_test)
print(f"✅ 训练完成")
print(f"R² score: {r2_score(y_test, y_pred):.4f}")
print(f"Mean Squared Error: {mean_squared_error(y_test, y_pred):.4f}")

# 示例预测（可换成新样本）
test_audio = os.path.join(data_dir, df.iloc[0]['filename'])
test_feat = extract_fluency_features(test_audio)
predicted_score = model.predict([list(test_feat.values())])[0]
print(f"🔍 示例预测文件: {df.iloc[0]['filename']}, 预测流利度分数: {predicted_score:.2f}")
