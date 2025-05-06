import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from test_voice import extract_fluency_features
# 引入上面定义的特征提取函数
# from your_module import extract_fluency_features

# 示例数据（你需要换成自己的）
audio_dir = "audio_files/"  # 包含音频的文件夹
labels = {  # 假设你有打分标签
    "audio1.wav": 4.5,
    "audio2.wav": 2.0,
    "audio3.wav": 3.8,
    # ...
}

X = []
y = []

# 提取每个音频的特征
for fname, score in labels.items():
    try:
        path = os.path.join(audio_dir, fname)
        features = extract_fluency_features(path)
        X.append(list(features.values()))
        y.append(score)
    except Exception as e:
        print(f"Error processing {fname}: {e}")

X = np.array(X)
y = np.array(y)

# 训练/测试划分
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 模型训练
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 模型预测与评估
y_pred = model.predict(X_test)

print("R² score:", r2_score(y_test, y_pred))
print("MSE:", mean_squared_error(y_test, y_pred))

# 预测新音频
# new_features = extract_fluency_features("new_audio.wav")
# print("Predicted fluency score:", model.predict([list(new_features.values())])[0])
