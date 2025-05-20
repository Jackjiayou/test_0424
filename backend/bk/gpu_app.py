import requests
import time
import os


def process_video(video_path, audio_path, api_url="http://117.50.91.160:8000"):
    """
    处理视频和音频文件

    参数:
        video_path: 视频文件路径（MP4格式）
        audio_path: 音频文件路径（WAV格式）
        api_url: API服务器地址
    """
    try:
        # 1. 上传文件并获取任务ID
        files = {
            'video_file': ('input.mp4', open(video_path, 'rb'), 'video/mp4'),
            'audio_file': ('input.wav', open(audio_path, 'rb'), 'audio/wav')
        }

        print("开始上传文件...")
        response = requests.post(f"{api_url}/process/", files=files)
        if response.status_code != 200:
            print(f"上传失败: {response.text}")
            return

        task_id = response.json()['task_id']
        print(f"文件上传成功，任务ID: {task_id}")

        # 2. 循环检查处理状态
        while True:
            status_response = requests.get(f"{api_url}/status/{task_id}")
            status = status_response.json()
            print(f"当前状态: {status['status']}")

            if status['status'] == 'completed':
                # 3. 下载处理完成的视频
                print("处理完成，开始下载结果...")
                result_response = requests.get(f"{api_url}/result/{task_id}")

                if result_response.status_code == 200:
                    output_path = f"output_{os.path.basename(video_path)}"
                    with open(output_path, 'wb') as f:
                        f.write(result_response.content)
                    print(f"下载完成，保存到: {output_path}")
                    return output_path
                else:
                    print(f"下载失败: {result_response.text}")
                break

            elif status['status'] == 'failed':
                print(f"处理失败: {status.get('error', '未知错误')}")
                break

            time.sleep(5)  # 每5秒检查一次状态

    except Exception as e:
        print(f"发生错误: {str(e)}")


def synthesize(text):
    """
    根据文本合成视频
    参数:
        text: 文本内容
    返回:
        video_url: 合成视频的URL
    """
    try:
        # 1. 调用文本转语音API，生成音频文件
        audio_path = text_to_speech(text)  # 假设text_to_speech函数已实现，返回音频文件路径

        # 2. 使用默认视频模板
        video_path = "E:\\work\\虚拟人\\hr.mp4"  # 默认视频模板路径

        # 3. 调用process_video合成视频
        output_path = process_video(video_path, audio_path)
        if output_path:
            # 4. 返回视频URL
            return f"http://182.92.109.197/download/{os.path.basename(output_path)}"
        else:
            raise Exception("视频合成失败")
    except Exception as e:
        print(f"合成视频失败: {str(e)}")
        return None


# 使用示例
if __name__ == "__main__":
    video_path = r"E:\work\虚拟人\hr.mp4"  # 你的视频文件路径
    audio_path = r"E:\work\虚拟人\1747033032.mp3"  # 你的音频文件路径

    output_path = process_video(video_path, audio_path)
    if output_path:
        print(f"处理成功，输出文件：{output_path}")