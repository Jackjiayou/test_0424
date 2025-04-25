# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import os
import time
import requests
import urllib

lfasr_host = 'https://raasr.xfyun.cn/v2/api'
# 请求的接口名
api_upload = '/upload'
api_get_result = '/getResult'


class RequestApi(object):
    def __init__(self, appid, secret_key, upload_file_path):
        self.appid = appid
        self.secret_key = secret_key
        self.upload_file_path = upload_file_path
        self.ts = str(int(time.time()))
        self.signa = self.get_signa()

    def get_signa(self):
        appid = self.appid
        secret_key = self.secret_key
        m2 = hashlib.md5()
        m2.update((appid + self.ts).encode('utf-8'))
        md5 = m2.hexdigest()
        md5 = bytes(md5, encoding='utf-8')
        # 以secret_key为key, 上面的md5为msg， 使用hashlib.sha1加密结果为signa
        signa = hmac.new(secret_key.encode('utf-8'), md5, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        return signa


    def upload(self):
        print("上传部分：")
        upload_file_path = self.upload_file_path
        file_len = os.path.getsize(upload_file_path)
        file_name = os.path.basename(upload_file_path)

        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict["fileSize"] = file_len
        param_dict["fileName"] = file_name
        param_dict["duration"] = "200"
        print("upload参数：", param_dict)
        data = open(upload_file_path, 'rb').read(file_len)

        response = requests.post(url =lfasr_host + api_upload+"?"+urllib.parse.urlencode(param_dict),
                                headers = {"Content-type":"application/json"},data=data)
        print("upload_url:",response.request.url)
        result = json.loads(response.text)
        print("upload resp:", result)
        return result


    def get_result(self):
        uploadresp = self.upload()
        orderId = uploadresp['content']['orderId']
        param_dict = {}
        param_dict['appId'] = self.appid
        param_dict['signa'] = self.signa
        param_dict['ts'] = self.ts
        param_dict['orderId'] = orderId
        param_dict['eng_smoothproc'] = True
        param_dict['eng_colloqproc'] = True
        param_dict['resultType'] = "transfer"
        print("")
        print("查询部分：")
        print("get result参数：", param_dict)
        status = 3
        # 建议使用回调的方式查询结果，查询接口有请求频率限制
        while status == 3:
            response = requests.post(url=lfasr_host + api_get_result + "?" + urllib.parse.urlencode(param_dict),
                                     headers={"Content-type": "application/json"})
            # print("get_result_url:",response.request.url)
            result = json.loads(response.text)
            print(result)
            status = result['content']['orderInfo']['status']
            print("status=",status)
            if status == 4:
                break
            time.sleep(5)
        print("get_result resp:",result)
        return result


def extract_words_from_lattice2(data):
    """提取lattice2中的文字内容并按时间顺序拼接"""
    # 获取所有段落并按开始时间排序
    segments = sorted(data['lattice2'], key=lambda x: int(x['begin']))

    text_parts = []
    for seg in segments:
        words = []
        # 遍历语音识别结果的多层结构
        for rt in seg['json_1best']['st']['rt']:
            for ws in rt['ws']:
                for cw in ws['cw']:
                    if cw['w']:  # 过滤空字符
                        words.append(cw['w'])
        # 合并当前时间段的文字
        text_parts.append(''.join(words))

    # 合并所有时间段文字
    return ''.join(text_parts)

# 输入讯飞开放平台的appid，secret_key和待转写的文件路径
if __name__ == '__main__':
    api = RequestApi(appid="5f30a0b3",
                     secret_key="dbfdebbd6299533f00fa97c6e8d1b008",
                     upload_file_path=r"audio/voice_1745203883261.mp3",
                     )

    result = api.get_result()

    if len(result) == 0:
        print("receive result end")

    result1 = json.loads(result['content']['orderResult'])

    # 解析结果

    # 解析JSON数据
    #data = json.loads(result1['lattice'][0]['json_1best'])
    str_result = extract_words_from_lattice2(result1)
    print(1)




    print(1)