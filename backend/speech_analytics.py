import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import threading
import queue
import uuid


class SpeechEvaluator:
    def __init__(self, appid, api_secret, api_key):
        self.appid = appid
        self.api_secret = api_secret
        self.api_key = api_key
        self.host_url = "ws://ise-api.xfyun.cn/v2/open-ise"
        # 使用字典存储每个请求的结果，key为请求ID
        self.results = {}
        # 使用锁来保护结果字典的访问
        self.results_lock = threading.Lock()
        # 使用事件来通知结果就绪
        self.result_events = {}
        # 使用锁来保护事件字典的访问
        self.events_lock = threading.Lock()

    def _generate_url(self):
        now_time = datetime.now()
        now_date = format_date_time(mktime(now_time.timetuple()))
        origin_base = "host: " + "ise-api.xfyun.cn" + "\n"
        origin_base += "date: " + now_date + "\n"
        origin_base += "GET " + "/v2/open-ise " + "HTTP/1.1"

        signature_sha = hmac.new(self.api_secret.encode('utf-8'), origin_base.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        dict_data = {
            "authorization": authorization,
            "date": now_date,
            "host": "ise-api.xfyun.cn"
        }
        return self.host_url + '?' + urlencode(dict_data)

    def _on_message(self, ws, message, request_id):
        print(f"Received message for request {request_id}: {message}")
        status = json.loads(message)["data"]["status"]
        if status == 2:
            xml = base64.b64decode(json.loads(message)["data"]["data"])
            result = xml.decode("utf-8")
            # 使用锁保护结果存储
            with self.results_lock:
                self.results[request_id] = result
            # 通知等待的线程结果已就绪
            with self.events_lock:
                if request_id in self.result_events:
                    self.result_events[request_id].set()
            ws.close()

    def _on_error(self, ws, error, request_id):
        print(f"Error for request {request_id}: {error}")
        # 存储错误结果
        with self.results_lock:
            self.results[request_id] = None
        # 通知等待的线程
        with self.events_lock:
            if request_id in self.result_events:
                self.result_events[request_id].set()

    def _on_close(self, ws, reason, res, request_id):
        print(f"WebSocket connection closed for request {request_id}")

    def _on_open(self, ws, text, audio_file, request_id):
        print(f"WebSocket connection opened for request {request_id}")
        send_dict = {
            "common": {
                "app_id": self.appid
            },
            "business": {
                "category": "read_sentence",
                "rstcd": "utf8",
                "sub": "ise",
                "group": "pupil",
                "ent": "cn_vip",
                "tte": "utf-8",
                "cmd": "ssb",
                "auf": "audio/L16;rate=16000",
                "aue": "raw",
                "text": '\uFEFF' + "[content]\n" + text
            },
            "data": {
                "status": 0,
                "data": ""
            }
        }
        ws.send(json.dumps(send_dict))

        try:
            with open(audio_file, "rb") as file_flag:
                while True:
                    buffer = file_flag.read(1280)
                    if not buffer:
                        my_dict = {"business": {"cmd": "auw", "aus": 4, "aue": "raw"},
                                   "data": {"status": 2, "data": str(base64.b64encode(buffer).decode())}}
                        ws.send(json.dumps(my_dict))
                        print(f"发送最后一帧 for request {request_id}")
                        time.sleep(1)
                        break
                    send_dict = {
                        "business": {
                            "cmd": "auw",
                            "aus": 1,
                            "aue": "raw"
                        },
                        "data": {
                            "status": 1,
                            "data": str(base64.b64encode(buffer).decode()),
                            "data_type": 1,
                            "encoding": "raw"
                        }
                    }
                    ws.send(json.dumps(send_dict))
                    time.sleep(0.04)
        except Exception as e:
            print(f"Error reading audio file for request {request_id}: {str(e)}")
            with self.results_lock:
                self.results[request_id] = None
            with self.events_lock:
                if request_id in self.result_events:
                    self.result_events[request_id].set()

    def evaluate(self, text: str, audio_file_path: str, timeout: int = 30) -> str:
        """
        评估语音与文本的匹配度

        Args:
            text (str): 要评估的文本内容
            audio_file_path (str): 音频文件的路径
            timeout (int): 超时时间（秒）

        Returns:
            str: 评估结果的XML字符串，如果发生错误则返回None
        """
        # 为每个请求生成唯一ID
        request_id = str(uuid.uuid4())

        try:
            # 创建事件对象用于等待结果
            with self.events_lock:
                self.result_events[request_id] = threading.Event()

            websocket.enableTrace(False)
            ws_url = self._generate_url()

            # 创建WebSocket连接
            ws = websocket.WebSocketApp(
                ws_url,
                on_message=lambda ws, msg: self._on_message(ws, msg, request_id),
                on_error=lambda ws, err: self._on_error(ws, err, request_id),
                on_close=lambda ws, reason, res: self._on_close(ws, reason, res, request_id),
                on_open=lambda ws: self._on_open(ws, text, audio_file_path, request_id)
            )

            # 在新线程中运行WebSocket连接
            ws_thread = threading.Thread(target=ws.run_forever, kwargs={"sslopt": {"cert_reqs": ssl.CERT_NONE}})
            ws_thread.daemon = True
            ws_thread.start()

            # 等待结果或超时
            with self.events_lock:
                event = self.result_events[request_id]

            if event.wait(timeout):
                with self.results_lock:
                    result = self.results.get(request_id)
            else:
                print(f"Request {request_id} timed out")
                result = None

            return result

        except Exception as e:
            print(f"语音评测发生错误 for request {request_id}: {str(e)}")
            return None
        finally:
            # 清理资源
            with self.results_lock:
                self.results.pop(request_id, None)
            with self.events_lock:
                self.result_events.pop(request_id, None)


# 使用示例
if __name__ == '__main__':
    # 配置信息
    APPID = "5e11538f"
    API_SECRET = "ff446b96b01252f80331ae6e4c64984a"
    API_KEY = "91205afe0d17e38c61be35fca346503c"

    # 创建评测器实例
    evaluator = SpeechEvaluator(APPID, API_SECRET, API_KEY)

    # 测试用例
    test_text = "我们的商品是核苷酸，公司的名字叫双迪，他和珍奥是一家集团，好了"
    test_audio = r"E:\work\code\test_uniapp\test_0424\backend\uploads\voice\卡曼公司是双迪.wav"

    # 执行评测
    start_time = datetime.now()
    result = evaluator.evaluate(test_text, test_audio)
    end_time = datetime.now()

    print(f"评测结果: {result}")
    print(f"评测耗时： {end_time - start_time}")