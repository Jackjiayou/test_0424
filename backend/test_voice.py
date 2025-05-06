import librosa
import numpy as np

def extract_fluency_features(audio_path):
    # 加载音频文件
    y, sr = librosa.load(audio_path, sr=None)

    # 帧级参数（帧长 2048，跳帧 512）
    hop_length = 512
    frame_length = 2048

    # 1. MFCC（可用于分析发音清晰度、音素变化）
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_delta = librosa.feature.delta(mfccs)
    mfcc_delta_std = np.std(mfcc_delta)

    # 2. 能量（RMS）用于估算停顿
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    avg_rms = np.mean(rms)
    num_pauses = np.sum(rms < 0.02)  # 低能量帧数，估算停顿

    # 3. Zero-Crossing Rate（用于无声段检测、修正语音等）
    zcr = librosa.feature.zero_crossing_rate(y=y, frame_length=frame_length, hop_length=hop_length)[0]
    avg_zcr = np.mean(zcr)

    # 4. 语速（估算发声段总长度 vs 整体长度）
    duration = librosa.get_duration(y=y, sr=sr)
    voiced_ratio = np.sum(rms > 0.02) * hop_length / sr / duration  # 发声段占比
    speech_rate_estimate = voiced_ratio / duration  # 越大可能越流利

    # 输出特征
    return {
        'mfcc_delta_std': mfcc_delta_std,
        'avg_rms': avg_rms,
        'num_pauses': num_pauses,
        'avg_zcr': avg_zcr,
        'voiced_ratio': voiced_ratio,
        'speech_rate_estimate': speech_rate_estimate,
        'duration_sec': duration
    }

# 示例使用
audio_path = r"E:\work\code\test_uniapp\test_0424\backend\uploads\voice\介绍双迪标准.wav"
features = extract_fluency_features(audio_path)

for k, v in features.items():
    print(f"{k}: {v:.4f}")
# mfcc_delta_std：MFCC 变化越平滑，说明语音更连贯；
#
# avg_rms：平均能量，反映语音强度；
#
# num_pauses：停顿帧数量，多说明卡顿；
#
# avg_zcr：频繁交叉可能与修正词或嘈杂音有关；
#
# voiced_ratio：说话时间占总时间比例；
#
# speech_rate_estimate：估算语速（纯估算）。