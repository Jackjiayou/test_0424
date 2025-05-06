import numpy as np
import librosa
import parselmouth
from flask import Flask, request, jsonify
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads/test"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=16000)

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_std = np.std(mfcc, axis=1)

    snd = parselmouth.Sound(file_path)
    pitch = snd.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    pitch_values = pitch_values[pitch_values > 0]

    pitch_mean = np.mean(pitch_values) if len(pitch_values) > 0 else 0
    pitch_std = np.std(pitch_values) if len(pitch_values) > 0 else 0

    formants = snd.to_formant_burg()
    f1_list, f2_list = [], []
    for t in np.arange(0.1, min(1.0, snd.duration), 0.1):
        f1 = formants.get_value_at_time(1, t)
        f2 = formants.get_value_at_time(2, t)
        if f1 and f2:
            f1_list.append(f1)
            f2_list.append(f2)

    f1_mean = np.mean(f1_list) if f1_list else 0
    f2_mean = np.mean(f2_list) if f2_list else 0

    return {
        "mfcc_std_mean": float(np.mean(mfcc_std)),
        "pitch_mean": float(pitch_mean),
        "pitch_std": float(pitch_std),
        "f1": float(f1_mean),
        "f2": float(f2_mean)
    }


def score_features(features):
    scores = {}

    # 连贯性（MFCC稳定度）
    scores["fluency"] = max(0, 100 - features["mfcc_std_mean"] * 10)

    # 音调自然度
    if 100 < features["pitch_mean"] < 300:
        scores["intonation"] = 100 - min(features["pitch_std"], 30)
    else:
        scores["intonation"] = 50

    # 发音准确性（Formant范围判断）
    if 400 < features["f1"] < 800 and 1200 < features["f2"] < 2500:
        scores["pronunciation"] = 95
    else:
        scores["pronunciation"] = 60

    # 平均总分
    scores["overall"] = round((scores["fluency"] + scores["intonation"] + scores["pronunciation"]) / 3, 1)
    return scores

@app.route("/score", methods=["POST"])
def score_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    file = request.files['audio']
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)

    try:
        features = extract_features(save_path)
        scores = score_features(features)
        return jsonify({
            "features": features,
            "scores": scores
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

