import requests
import datetime
import hashlib
import base64
import hmac
import os
import re
import time
import  json
from fileupload import seve_file

class SpeechToText:
    def __init__(self, app_id, api_key, api_secret):
        """
        初始化语音转文字服务
        
        Args:
            app_id (str): 讯飞开放平台应用ID
            api_key (str): 讯飞开放平台API Key
            api_secret (str): 讯飞开放平台API Secret
        """
        self.Host = "ost-api.xfyun.cn"
        self.RequestUriCreate = "/v2/ost/pro_create"
        self.RequestUriQuery = "/v2/ost/query"
        
        # 设置url
        if re.match("^\d", self.Host):
            self.urlCreate = "http://" + self.Host + self.RequestUriCreate
            self.urlQuery = "http://" + self.Host + self.RequestUriQuery
        else:
            self.urlCreate = "https://" + self.Host + self.RequestUriCreate
            self.urlQuery = "https://" + self.Host + self.RequestUriQuery
            
        self.APPID = app_id
        self.APIKey = api_key
        self.APISecret = api_secret
        self.HttpMethod = "POST"
        self.Algorithm = "hmac-sha256"
        self.HttpProto = "HTTP/1.1"

    def _get_date(self):
        """获取当前UTC时间"""
        cur_time_utc = datetime.datetime.utcnow()
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][cur_time_utc.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec"][cur_time_utc.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (
            weekday, cur_time_utc.day, month, cur_time_utc.year,
            cur_time_utc.hour, cur_time_utc.minute, cur_time_utc.second)

    def _hashlib_256(self, res):
        """计算SHA-256哈希值"""
        m = hashlib.sha256(bytes(res.encode(encoding='utf-8'))).digest()
        return "SHA-256=" + base64.b64encode(m).decode(encoding='utf-8')

    def _generate_signature(self, digest, uri):
        """生成签名"""
        signature_str = "host: " + self.Host + "\n"
        signature_str += "date: " + self._get_date() + "\n"
        signature_str += self.HttpMethod + " " + uri + " " + self.HttpProto + "\n"
        signature_str += "digest: " + digest
        
        signature = hmac.new(bytes(self.APISecret.encode('utf-8')),
                           bytes(signature_str.encode('utf-8')),
                           digestmod=hashlib.sha256).digest()
        return base64.b64encode(signature).decode(encoding='utf-8')

    def _init_header(self, data, uri):
        """初始化请求头"""
        digest = self._hashlib_256(data)
        sign = self._generate_signature(digest, uri)
        
        auth_header = 'api_key="%s",algorithm="%s", headers="host date request-line digest", signature="%s"' % (
            self.APIKey, self.Algorithm, sign)
            
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Method": "POST",
            "Host": self.Host,
            "Date": self._get_date(),
            "Digest": digest,
            "Authorization": auth_header
        }

    def _get_create_body(self, file_url):
        """获取创建任务的请求体"""
        return json.dumps({
            "common": {"app_id": self.APPID},
            "business": {
                "language": "zh_cn",
                "accent": "mandarin",
                "domain": "pro_ost_ed",
            },
            "data": {
                "audio_src": "http",
                "audio_url": file_url,
                "encoding": "raw"
            }
        })

    def _get_query_body(self, task_id):
        """获取查询任务的请求体"""
        return json.dumps({
            "common": {"app_id": self.APPID},
            "business": {"task_id": task_id}
        })

    def _call_api(self, url, body, headers):
        """调用API"""
        try:
            response = requests.post(url, data=body, headers=headers, timeout=8)
            if response.status_code != 200:
                raise Exception(f"API调用失败: {response.content}")
            return json.loads(response.text)
        except Exception as e:
            raise Exception(f"API调用出错: {str(e)}")

    def _upload_file(self, file_path):
        """上传文件到讯飞服务器"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"音频文件不存在：{file_path}")
            
        api = seve_file.SeveFile(
            app_id=self.APPID,
            api_key=self.APIKey,
            api_secret=self.APISecret,
            upload_file_path=file_path
        )
        
        file_total_size = os.path.getsize(file_path)
        if file_total_size < 31457280:  # 30MB
            return api.gene_params('/upload')['data']['url']
        else:
            return api.gene_params('/mpupload/upload')

    def recognize(self, audio_file):
        """
        识别音频文件
        
        Args:
            audio_file (str): 音频文件路径
            
        Returns:
            str: 识别出的文字
            
        Raises:
            FileNotFoundError: 音频文件不存在
            Exception: 识别过程中发生错误
        """
        try:
            # 上传文件
            print("正在上传音频文件...")
            file_url = self._upload_file(audio_file)
            
            # 创建任务
            print("正在创建识别任务...")
            create_body = self._get_create_body(file_url)
            create_headers = self._init_header(create_body, self.RequestUriCreate)
            create_result = self._call_api(self.urlCreate, create_body, create_headers)
            
            if 'data' not in create_result or 'task_id' not in create_result['data']:
                raise Exception("创建任务失败")
                
            task_id = create_result['data']['task_id']
            
            # 查询任务结果
            print("正在识别音频...")
            while True:
                query_body = self._get_query_body(task_id)
                query_headers = self._init_header(query_body, self.RequestUriQuery)
                result = self._call_api(self.urlQuery, query_body, query_headers)
                
                if not isinstance(result, dict):
                    raise Exception(f"查询结果格式错误: {result}")
                    
                task_status = result['data'].get('task_status')
                if task_status not in ['1', '2']:  # 1: 处理中, 2: 排队中
                    if task_status == '3':  # 3: 失败
                        raise Exception(f"识别失败: {result}")
                    elif task_status == '4':  # 4: 完成
                        return result['data'].get('result', '')
                        
                time.sleep(2)  # 等待2秒后再次查询
                
        except Exception as e:
            raise Exception(f"语音识别失败: {str(e)}")

def speech_to_text(audio_file, app_id, api_key, api_secret):
    """
    将音频文件转换为文字
    
    Args:
        audio_file (str): 音频文件路径
        app_id (str): 讯飞开放平台应用ID
        api_key (str): 讯飞开放平台API Key
        api_secret (str): 讯飞开放平台API Secret
        
    Returns:
        str: 识别出的文字
        
    Raises:
        FileNotFoundError: 音频文件不存在
        Exception: 识别过程中发生错误
    """
    stt = SpeechToText(app_id, api_key, api_secret)
    return stt.recognize(audio_file)

if __name__ == "__main__":
    # 测试代码
    APP_ID = "5f30a0b3"
    API_KEY = "d4070941076c1e019907487878384f6c"
    API_SECRET = "MGYyMzJlYmYzZWVmMjIxZWE4ZThhNzA4"
    local_url = r".\uploads\tts\1745980823.mp3"
    local_url = r'.\uploads\voice\今天是星期几_16k.wav'
    #audio_1745982238812_bvse6m_16k  audio_1745981871245_gq2j8n_16k
    try:
        result = speech_to_text(local_url, APP_ID, API_KEY, API_SECRET)
        print("识别结果：", result)
    except Exception as e:
        print(f"识别失败：{e}") 