from fastapi import FastAPI, HTTPException,   Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import json
import random
from datetime import datetime
import uuid
from  personification_text_to_speach import  text_to_speech
import getds
from  speech_to_text_fast   import  speech_to_text as st
import  traceback
import librosa
from pydub import AudioSegment
from pydub.utils import which
import logging
import requests
import time
import os
from  search_vectorDB import  vector_search

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
base_url = "http://localhost:8000"  # 开发环境
#base_url = "https://ai.dl-dd.com"  # 生产环境

APP_ID = "5f30a0b3"
API_KEY = "d4070941076c1e01997487878384f6c"
API_SECRET = "MGYyMzJlYmYzZWVmMjIxZWE4ZThhNzA4"


# 创建FastAPI应用
app = FastAPI(title="销售培训API", description="销售培训小程序后端API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，实际生产环境应限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 修改文件路径，使用os.path.join确保跨平台兼容
# 确保上传目录存在
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "tts"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "voice"), exist_ok=True)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")), name="static")
# 挂载上传目录，用于访问语音文件
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

#
# # 确保上传目录存在
# os.makedirs("uploads", exist_ok=True)
# os.makedirs("uploads/tts", exist_ok=True)
# os.makedirs("uploads/voice", exist_ok=True)
# # 挂载静态文件目录
# app.mount("/static", StaticFiles(directory="."), name="static")
# # 挂载上传目录，用于访问语音文件
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# 创建用户和对话相关的目录结构
def ensure_user_dirs(user_id: str, conversation_id: str):
    # 用户目录
    user_dir = f"uploads/users/{user_id}"
    os.makedirs(user_dir, exist_ok=True)

    # 对话目录
    conversation_dir = f"{user_dir}/conversations/{conversation_id}"
    os.makedirs(f"{conversation_dir}/tts", exist_ok=True)
    os.makedirs(f"{conversation_dir}/voice", exist_ok=True)

    return conversation_dir


# 添加直接访问音频文件的路由
@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    file_path = f"uploads/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/wav")
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")

# 定义数据模型
class Scene(BaseModel):
    id: int
    name: str
    description: str
    goal: str
    icon: str

class Question(BaseModel):
    id: int
    sceneId: int
    text: str
    voiceUrl: str
    duration: str

class Message(BaseModel):
    from_user: str  # 'user' 或 'robot'
    text: str
    voiceUrl: str
    duration: str
    timestamp: datetime
    suggestion: Optional[str] = None

class Report(BaseModel):
    id: str
    sceneId: int
    userId: str
    overall: int
    dimensions: Dict[str, int]
    analysis: Dict[str, Dict[str, Any]]
    suggestions: List[str]
    createdAt: datetime

# 模拟数据
scenes = [
    {
        "id": 0,
        "name": "核苷酸产品介绍",
        "description": "你是一位珍奥双迪的保健品销售，正在对保健品持怀疑态度且较为节俭的中老年客户，重点推广核苷酸产品",
        "goal": "通过科学依据和产品优势打消客户疑虑，促使选择购买珍奥的核苷酸产品。",
        "icon": "/static/scene1.png"
    },
    {
        "id": 1,
        "name": "新客户开发",
        "description": "针对首次接触的潜在客户，学习如何有效地介绍产品和建立信任。本场景模拟与一位对产品完全陌生的客户进行初次沟通，你需要通过有效的自我介绍和产品展示，引起客户的兴趣。",
        "goal": "学习如何快速建立与新客户的信任关系，引起客户对产品的兴趣，为后续的深入交流奠定基础。",
        "icon": "/static/scene1.png"
    },
    {
        "id": 2,
        "name": "异议处理",
        "description": "学习如何面对客户提出的各种异议，并有效地进行回应。在销售过程中，客户常常会提出各种疑问和异议，本场景将帮助你学习如何处理这些问题，并将潜在的阻碍转化为销售机会。",
        "goal": "掌握处理客户异议的技巧，将异议转化为销售机会，提高客户的购买意愿。",
        "icon": "/static/scene2.png"
    },
    {
        "id": 3,
        "name": "产品推荐",
        "description": "根据客户需求，推荐最合适的产品，提高销售成功率。本场景模拟客户已经表明了自己的需求，你需要基于这些需求，向客户推荐最合适的产品。",
        "goal": "学习如何精准分析客户需求，进行有针对性的产品推荐，提高客户满意度和购买几率。",
        "icon": "/static/scene3.png"
    },
    {
        "id": 4,
        "name": "成交技巧",
        "description": "学习如何引导客户做出购买决定，顺利完成销售。本场景模拟客户已经对产品有较高兴趣，但尚未做出购买决定的情况，你需要运用成交技巧，促使客户完成购买。",
        "goal": "掌握成交的时机把握和话术技巧，提高成交率，顺利完成销售过程。",
        "icon": "/static/scene4.png"
    }
]

# 问题库
questions = {
    0: [  # 新客户开发
        {
            "id": 1,
            "sceneId": 0,
            "text": "我现在很年轻，平常很注重食疗，现在身体状态很不错，我现在真的需要保健吗？",
            "voiceUrl": "/static/audio/scene1-q1.mp3",
            "duration": "5"
        },
        {
            "id": 2,
            "sceneId": 0,
            "text": "这个产品我吃完以后能有什么效果或者改善呢？",
            "voiceUrl": "/static/audio/scene1-q2.mp3",
            "duration": "4"
        },
        {
            "id": 3,
            "sceneId": 0,
            "text": "我有很多保健品的选择，为什么要选择你们的核苷酸呢？",
            "voiceUrl": "/static/audio/scene1-q3.mp3",
            "duration": "5"
        }
    ],
    1: [  # 新客户开发
        {
            "id": 1,
            "sceneId": 1,
            "text": "您好，听说贵公司有一些不错的产品，能简单介绍一下吗？",
            "voiceUrl": "/static/audio/scene1-q1.mp3",
            "duration": "5"
        },
        {
            "id": 2,
            "sceneId": 1,
            "text": "我还不太了解你们公司的背景，能告诉我你们公司的情况吗？",
            "voiceUrl": "/static/audio/scene1-q2.mp3",
            "duration": "4"
        },
        {
            "id": 3,
            "sceneId": 1,
            "text": "市场上类似的产品很多，贵公司的产品有什么特别之处吗？",
            "voiceUrl": "/static/audio/scene1-q3.mp3",
            "duration": "5"
        }
    ],
    2: [  # 异议处理
        {
            "id": 4,
            "sceneId": 2,
            "text": "这个价格对我来说有点高，能便宜一些吗？",
            "voiceUrl": "/static/audio/scene2-q1.mp3",
            "duration": "3"
        },
        {
            "id": 5,
            "sceneId": 2,
            "text": "我以前用过类似的产品，但效果不太理想，为什么我要选择你们的呢？",
            "voiceUrl": "/static/audio/scene2-q2.mp3",
            "duration": "6"
        },
        {
            "id": 6,
            "sceneId": 2,
            "text": "我需要考虑一下，可以过几天再联系你吗？",
            "voiceUrl": "/static/audio/scene2-q3.mp3",
            "duration": "4"
        }
    ],
    3: [  # 产品推荐
        {
            "id": 7,
            "sceneId": 3,
            "text": "我需要一个能提高团队效率的工具，你们有什么推荐？",
            "voiceUrl": "/static/audio/scene3-q1.mp3",
            "duration": "4"
        },
        {
            "id": 8,
            "sceneId": 3,
            "text": "我预算有限，有什么性价比高的选择吗？",
            "voiceUrl": "/static/audio/scene3-q2.mp3",
            "duration": "3"
        },
        {
            "id": 9,
            "sceneId": 3,
            "text": "我们团队有20人，有适合团队使用的套餐吗？",
            "voiceUrl": "/static/audio/scene3-q3.mp3",
            "duration": "4"
        }
    ],
    4: [  # 成交技巧
        {
            "id": 10,
            "sceneId": 4,
            "text": "我对产品很满意，但现在签合同是不是太仓促了？",
            "voiceUrl": "/static/audio/scene4-q1.mp3",
            "duration": "4"
        },
        {
            "id": 11,
            "sceneId": 4,
            "text": "如果我现在决定购买，有什么优惠吗？",
            "voiceUrl": "/static/audio/scene4-q2.mp3",
            "duration": "3"
        },
        {
            "id": 12,
            "sceneId": 4,
            "text": "购买后如果不满意，能退款吗？",
            "voiceUrl": "/static/audio/scene4-q3.mp3",
            "duration": "3"
        }
    ]
}

# 改进建议模板
suggestion_templates = [
    "您的表达可以更加简洁明了，建议减少重复词语，直接表达核心信息。",
    "可以使用更专业的术语来增强可信度，比如将'很好的产品'改为'高性价比的解决方案'。",
    "回答时可以加入一些数据支持，增强说服力，例如'我们的产品已帮助超过1000家企业提升了30%的效率'。",
    "语速过快，建议适当放慢并在关键点停顿，让客户有时间消化信息。",
    "可以先认同客户的顾虑，再提出解决方案，如'您提到的价格问题很重要，我们可以...'。"
]

# 存储报告的字典
reports = {}

def convert_mp3_16k(audio_path):
    AudioSegment.converter = which("ffmpeg")  # 这句很关键！
    audio = AudioSegment.from_file(audio_path)
    # 设置采样率和声道
    # audio = audio.set_frame_rate(16000).set_channels(1)
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    base, _ = os.path.splitext(audio_path)
    output_path = base + "_16k.mp3"

    # 导出音频
    audio.export(output_path, format="mp3")

    return os.path.basename(output_path)

# API路由
    
@app.get("/test")
async def root():
    return {"message": "销售培训API服务运行正常"}

@app.get("/scenes", response_model=List[dict])
async def get_scenes():
    return scenes

@app.get("/scenes/{scene_id}", response_model=dict)
async def get_scene(scene_id: int):
    scene = next((s for s in scenes if s["id"] == scene_id), None)
    if not scene:
        raise HTTPException(status_code=404, detail=f"Scene {scene_id} not found")
    return scene

@app.get("/questions/{scene_id}", response_model=dict)
async def get_random_question(scene_id: int):
    if scene_id not in questions:
        raise HTTPException(status_code=404, detail=f"Questions for scene {scene_id} not found")
    
    scene_questions = questions[scene_id]
    if not scene_questions:
        raise HTTPException(status_code=404, detail=f"No questions available for scene {scene_id}")
    
    # 随机选择一个问题
    random_question = random.choice(scene_questions)
    return random_question

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

@app.post("/speech-to-text")
async def speech_to_text(audio_file: UploadFile = File(...), sceneId: int = Form(None), fileName: str = Form(None),
    userId: str = Form(...),
    conversationId: str = Form(...)):
    """
    将上传的语音文件转换为文本
    实际项目中应调用专业的语音识别API（如百度语音、讯飞语音等）
    
    此处为示例代码，真实实现时请替换为实际的语音识别API调用
    """
    # 使用传入的文件名或生成新的文件名
    if not fileName:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
        fileName = f"audio_{timestamp}_{random_str}.mp3"
    
    # 确保文件名有正确的扩展名
    if not fileName.endswith(('.wav', '.mp3', '.aac')):
        fileName += '.mp3'
    
    # 保存上传的文件
    file_location = f"uploads/voice/{fileName}"
    os.makedirs("uploads/voice", exist_ok=True)
    
    try:
        # 确保文件上传成功
        contents = await audio_file.read()
        with open(file_location, "wb") as f:
            f.write(contents)



        # 生成可访问的完整URL
        # 使用新的音频文件路由

        voice_url = f"{base_url}/uploads/voice/{fileName}"
        local_url = f"./uploads/voice/{fileName}"
        # TODO: 此处调用您自己的语音识别API
        # api = RequestApi(appid="5f30a0b3",
        #                  secret_key="dbfdebbd6299533f00fa97c6e8d1b008",
        #                  upload_file_path=local_url
        #                  )
        # result = api.get_result()
        # print(len(result))
        # if len(result) == 0:
        #     print("receive result end")
        # result1 = json.loads(result['content']['orderResult'])
        #
        # # 解析结果
        #
        # # 解析JSON数据
        # # data = json.loads(result1['lattice'][0]['json_1best'])
        # str_result = extract_words_from_lattice2(result1)


        APP_ID = "5f30a0b3"
        API_KEY = "d4070941076c1e019907487878384f6c"
        API_SECRET = "MGYyMzJlYmYzZWVmMjIxZWE4ZThhNzA4"
        #极速版
        #-----------------------------------------------------
        new_name = convert_mp3_16k(local_url)
        voice_url = f"{base_url}/uploads/voice/{new_name}"

        new_local_url = fileName.replace('.mp3','_16k.mp3')
        new_url = f"./uploads/voice/{new_name}"
        str_result = st(new_url, APP_ID, API_KEY, API_SECRET)
        str_result = extract_words_from_lattice2(str_result)
        #--------------------------------


        #------------------------------------------------
        #
        # str_result = st(local_url, APP_ID, API_KEY, API_SECRET)
        # str_result = extract_words_from_lattice2(str_result)
        #-----------------------------------------------------
        return {"text":str_result , "voiceUrl": voice_url}
    
    except Exception as e:
        logger.error(traceback.format_exc())
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"message": f"上传文件处理失败: {str(e)}"}
        )

# @app.post("/text-to-speech")
# async def text_to_speech(text: str = Form(...)):
#     """
#     将文本转换为语音
#     这里使用模拟数据，实际项目中应该调用语音合成API
#     """
#     # 模拟文字转语音的结果
#     return {
#         "voiceUrl": "/static/audio/response.mp3",
#         "duration": str(random.randint(3, 10))
#     }

@app.post("/analyze")
async def analyze_message(request: Dict[str, Any]):
    """
    分析用户消息并生成改进建议
    这里使用模拟数据，实际项目中应该调用大模型API
    """
    print("analyze_message start")
    message = request.get("message", "")
    scene_id = request.get("sceneId", 1)
    message_all = request['messages_all']
    msg = getds.get_messages_analyze(message_all)
    #prompt_str = message_all + "上面是我们的聊天记录，聊天记录中我的标签是user，你的标签是assistant，请明确区分你我的对话，不要把你的话当成我说的，我是一名大健康行业直销员，你是顾客，请对我的最后一句话的回答，生成改进建议,不需要给出分析，直接给出改进建议和示例"
    robot_words = getds.get_response(msg)



    # 随机选择一个建议模板
    suggestion = random.choice(suggestion_templates)
    print("analyze_message end")
    return {
        "suggestion": robot_words,
        "score": random.randint(70, 95)
    }

@app.post("/report")
async def generate_report(request: Dict[str, Any]):
    """
    生成练习报告
    这里使用模拟数据，实际项目中应该调用大模型API进行详细分析
    """
    scene_id = request.get("sceneId", 1)
    user_id = request.get("userId", "user1")
    messages = request.get("messages", [])
    
    # 创建一个唯一的报告ID
    report_id = f"report_{scene_id}_{uuid.uuid4().hex[:8]}"
    
    # 生成模拟报告数据
    report = {
        "id": report_id,
        "sceneId": scene_id,
        "userId": user_id,
        "overall": random.randint(75, 95),
        "dimensions": {
            "languageOrganization": random.randint(70, 90),
            "persuasiveness": random.randint(70, 90),
            "fluency": random.randint(70, 90),
            "accuracy": random.randint(70, 90),
            "expression": random.randint(70, 90)
        },
        "analysis": {
            "languageOrganization": {
                "score": random.randint(70, 90),
                "content": "您的语言组织整体较好，能够按照逻辑顺序表达自己的观点。但在某些回答中，内容结构可以更紧凑，减少不必要的铺垫。"
            },
            "persuasiveness": {
                "score": random.randint(70, 90),
                "content": "您在阐述产品优势时的说服力有待提高。建议增加具体数据和案例支持，让客户更容易接受您的观点。"
            },
            "fluency": {
                "score": random.randint(70, 90),
                "content": "您的语速适中，表达流畅，很少出现停顿或冗余词。在回答中，仅有少量的明显停顿，整体流利度表现良好。"
            },
            "accuracy": {
                "score": random.randint(70, 90),
                "content": "您对产品特性的描述基本准确，能够清晰地传达核心价值。但在解释某些技术细节时有轻微的不准确。"
            },
            "expression": {
                "score": random.randint(70, 90),
                "content": "您的语言表达整体清晰，用词专业，能够使用行业术语增强专业感。但有时用词略显重复，可以通过丰富词汇量来增加表达的多样性。"
            }
        },
        "suggestions": [
            "在回答客户问题前，可以先简短重复一下客户的问题，表明您理解了他们的需求。",
            "增加具体案例和数据支持，提高说服力。可以准备2-3个成功案例，在合适的时机分享。",
            "适当使用反问句引导客户思考，这样的问题可以引导客户从新的角度看问题。",
            "在谈到产品优势时，可以结合客户所处的行业情况，使建议更有针对性。",
            "练习如何简洁有力地总结对话内容，在每个销售环节结束时进行小结，帮助客户和自己明确当前进展。"
        ],
        "createdAt": datetime.now().isoformat()
    }
    
    # 保存报告
    reports[report_id] = report
    
    return {"reportId": report_id}

@app.get("/reports/{report_id}")
async def get_report(report_id: str):
    """
    获取指定ID的报告
    """
    if report_id not in reports:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    
    return reports[report_id]

@app.post("/polish-text")
async def polish_text(request: Dict[str, Any]):
    """
    润色用户表达
    这里使用模拟数据，实际项目中应该调用大模型API
    """
    text = request.get("text", "")
    scene_id = request.get("sceneId", 1)
    
    # 根据场景ID选择不同的润色模板
    polish_templates = {
        1: [  # 新客户开发
            "您好，我是XX公司的销售顾问。我们公司专注于提供高质量的销售培训解决方案，已经帮助超过1000家企业提升了30%的销售业绩。根据您的需求，我们的产品可以为您提供个性化的培训方案，帮助您的团队快速提升销售技能。",
            "感谢您的咨询。我们公司成立于2010年，专注于销售培训领域，拥有丰富的行业经验和专业的培训团队。我们的产品采用最新的AI技术，能够根据每个销售人员的表现提供个性化的改进建议，帮助团队整体提升销售能力。",
            "您提到的市场竞争问题很重要。与市场上其他产品相比，我们的优势在于更精准的数据分析和更全面的客户服务。我们的系统不仅提供培训，还能实时跟踪销售人员的表现，生成详细的报告，帮助管理层做出更明智的决策。"
        ],
        2: [  # 异议处理
            "关于价格问题，我完全理解您的考虑。我们的产品虽然初始投资较高，但长期来看，它能够帮助您的团队提高30%的销售效率，这意味着更多的收入和利润。此外，我们提供灵活的付款方案，可以根据您的预算进行调整。",
            "您提到的使用体验问题很有价值。我们最近对产品进行了全面升级，解决了之前用户反馈的问题。现在系统更加稳定，界面更加友好，而且我们提供7*24小时的技术支持，确保您在使用过程中遇到任何问题都能得到及时解决。",
            "我理解您需要时间考虑。这是一个重要的决定，确实需要慎重。不过，我想提醒您，我们目前正在进行限时优惠活动，如果您在本周内做出决定，可以享受20%的折扣。同时，我们提供30天无理由退款保证，您可以放心试用。"
        ],
        3: [  # 产品推荐
            "针对提高团队效率的需求，我推荐我们的'销售加速器'套餐。这个套餐包含完整的销售培训课程、实时表现分析工具和个性化辅导服务，能够帮助您的团队在短时间内提升销售技能和工作效率。根据我们客户的数据，使用这个套餐的团队平均在3个月内提升了25%的销售业绩。",
            "考虑到您的预算限制，我推荐我们的'基础提升'套餐。这个套餐虽然功能相对简单，但包含了最核心的销售技能培训和分析工具，性价比极高。我们还可以根据您的具体需求进行定制，确保您花的每一分钱都能带来最大的回报。",
            "对于20人的团队，我们的'团队协作'套餐是最佳选择。这个套餐专为中型团队设计，包含团队协作工具、集体培训课程和团队绩效分析报告。我们还可以为您的团队提供专属的客户经理，确保您获得最优质的服务和支持。"
        ],
        4: [  # 成交技巧
            "签合同并不仓促，而是对双方都有保障的正式承诺。我们的产品已经得到了市场的广泛认可，目前有超过1000家企业正在使用。如果您现在签约，不仅可以享受当前的优惠价格，还能立即开始使用我们的产品，帮助您的团队提升销售业绩。",
            "如果您现在决定购买，除了享受当前的折扣外，我们还可以为您提供3个月的免费技术支持服务，价值超过5000元。此外，我们还会为您的团队提供一次免费的销售技能评估，帮助您了解团队的现状和提升空间。",
            "我们对自己的产品非常有信心，因此提供30天无理由退款保证。如果您在使用过程中发现产品不符合您的需求，可以随时申请退款，我们会全额退还您的费用，没有任何附加条件。这充分体现了我们对产品质量的自信和对客户的尊重。"
        ]
    }
    
    # 选择对应场景的润色模板
    templates = polish_templates.get(scene_id, polish_templates[1])
    
    # 根据用户输入内容选择最相关的模板
    # 这里使用简单的关键词匹配，实际项目中可以使用更复杂的算法
    selected_template = templates[0]  # 默认使用第一个模板
    
    # 简单的关键词匹配逻辑
    keywords = {
        "价格": 0,
        "贵": 0,
        "便宜": 0,
        "优惠": 0,
        "折扣": 0,
        "公司": 1,
        "背景": 1,
        "成立": 1,
        "产品": 2,
        "特点": 2,
        "优势": 2,
        "特别": 2,
        "考虑": 3,
        "想想": 3,
        "再联系": 3,
        "签": 4,
        "合同": 4,
        "购买": 4,
        "退款": 5,
        "不满意": 5
    }
    
    # 查找匹配的关键词
    for keyword, index in keywords.items():
        if keyword in text and index < len(templates):
            selected_template = templates[index]
            break
    
    return {
        "polishedText": selected_template
    }

@app.get("/get-robot-message")
async def get_robot_message(sceneId: int, messageCount: int, messages: Optional[str] = None, userId: str = None, conversationId: str = None):
    """
    获取机器人消息
    
    参数:
    - sceneId: 场景ID
    - messageCount: 当前消息数量
    - messages: 历史消息记录（JSON字符串）
    
    返回:
    - text: 机器人消息文本
    - duration: 语音时长（秒）
    - voiceUrl: 语音文件URL
    """
    print('get_robot_message')
    print("get_robot_message start")
    # 确保上传目录存在
    os.makedirs("./uploads/tts", exist_ok=True)
    
    # 设置基础URL，使用单斜杠
    base_urlr = base_url+"/uploads/tts/"


    try:
        # 解析历史消息
        history_messages = []
        if messages:
            try:
                history_messages = json.loads(messages)
            except:
                pass
        
        # 获取场景名称
        scene_name = next((s["name"] for s in scenes if s["id"] == sceneId), "未知场景")
        
        # 模拟大模型生成回复
        # 在实际应用中，这里应该调用大模型API
        # 这里我们根据消息数量和场景ID选择不同的回复策略
        
        # 如果是第一条消息（初始问候）
        if messageCount == 0:
            # 从问题库中随机选择一个初始问题
            scene_questions = questions.get(sceneId, [])
            if scene_questions:
                question = random.choice(scene_questions)
                text = question["text"]
                file_path = './uploads/tts/'
                # file_name = text_to_speech(text,APP_ID,API_KEY,API_SECRET,file_path)
                APP_ID = '5f30a0b3'
                API_SECRET = 'MGYyMzJlYmYzZWVmMjIxZWE4ZThhNzA4'
                API_KEY = 'd4070941076c1e019907487878384f6c'
                file_name = text_to_speech(text, APP_ID, API_SECRET, API_KEY, file_path)
                logger.info(file_name)
                # 确保文件名不包含路径分隔符
                file_name = file_name = os.path.basename(file_name)

                y, sr = librosa.load(file_path+file_name, sr=None)

                # 计算音频时长（秒）
                duration = librosa.get_duration(y=y, sr=sr)
                duration=  round(duration)
                file_path_url = base_urlr+file_name
                #duration = question["duration"]
                return {
                    "text": text,
                    "duration": duration,
                    "voiceUrl": file_path_url
                }
            else:
                # 默认问候语
                text = f"您好！我是您的销售助手，很高兴为您服务。今天我们将练习{scene_name}场景。请问有什么可以帮助您的？"
                duration = "5"


        else:
            # 根据历史消息生成回复
            # 这里简单模拟，实际应用中应该调用大模型
            if len(history_messages) > 0:
                last_message = history_messages[-1]
                if last_message["from"] == "user":
                    # 根据用户最后一条消息生成回复
                    user_content = last_message["text"].lower()
                    #messages
                    #prompt_str = messages+ "上面是我们的聊天记录，聊天记录中我的标签是user，你的标签是assistant，请明确区分你我的对话，不要把你的话当成我说的，我是一名大健康行业直销员，你是顾客的角色，通过对我提问和交流，对我不用太客气，锻炼我与客户沟通能力，请你结合历史聊天记录对我提问交流，仅输出下段话就可以，你的话仅仅是对话内容"
                    #robot_words = getds.get_response(prompt_str)

                    chat_msg = getds.get_messages_ai(messages)
                    ddd=datetime.now()
                    robot_words = getds.get_response_qwen(chat_msg)
                    ddd1 = datetime.now()
                    robot_words1 = getds.get_response(chat_msg)
                    ddd2 = datetime.now()

                    print('1:'+str(ddd1-ddd))
                    print('1:' + str(ddd2 - ddd1))
                    APP_ID = '5f30a0b3'
                    API_SECRET = 'MGYyMzJlYmYzZWVmMjIxZWE4ZThhNzA4'
                    API_KEY = 'd4070941076c1e019907487878384f6c'

                    file_path = './uploads/tts/'
                    file_name = text_to_speech(robot_words,APP_ID,API_SECRET,API_KEY,file_path)
                    # 使用librosa加载音频文件
                    y, sr = librosa.load(file_path+file_name, sr=None)

                    # 计算音频时长（秒）
                    duration = librosa.get_duration(y=y, sr=sr)
                    duration = round(duration)
                    # 确保文件名不包含路径分隔符
                    file_name = os.path.basename(file_name)
                    file_path_url = base_urlr + file_name

                    return {
                        "text": robot_words,
                        "duration": round(int(duration)),
                        "voiceUrl": file_path_url
                    }
        
        # 模拟语音合成
        # 在实际应用中，这里应该调用语音合成API
        # 这里我们使用预定义的语音URL
        scene_questions = questions.get(sceneId, [])
        voice_urls_for_scene = [q["voiceUrl"] for q in scene_questions]
        if voice_urls_for_scene:
            voice_url = random.choice(voice_urls_for_scene)
        else:
            # 默认语音URL
            voice_url = f"https://example.com/audio/default.wav"
        print("get_robot_message end")
        # 返回结果
        return {
            "text": text,
            "duration": round(int(duration)),
            "voiceUrl": voice_url
        }
    
    except Exception as e:
        logger.error( traceback.format_exc())
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取机器人消息失败: {str(e)}")

@app.post("/digital-human-speech-to-text")
async def digital_human_speech_to_text(audio_file: UploadFile = File(...), userId: str = Form(...), conversationId: str = Form(...)):
    """
    珍迪助手页面的语音转文字接口
    复用 /speech-to-text 的逻辑，但返回格式更简单
    """
    try:
        # 复用 /speech-to-text 的逻辑
        result = await speech_to_text(audio_file, None, None, userId, conversationId)
        return result
    except Exception as e:
        logger.error(traceback.format_exc())
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": f"语音转文字失败: {str(e)}"})

@app.get("/digital-human-robot-message")
async def digital_human_robot_message(sceneId: int, messageCount: int, messages: Optional[str] = None, userId: str = None, conversationId: str = None):
    """
    珍迪助手页面的机器人回复接口
    复用 /get-robot-message 的逻辑，但返回格式更简单
    """
    try:
        # 复用 /get-robot-message 的逻辑
        result = await get_robot_message(sceneId, messageCount, messages, userId, conversationId)
        return result
    except Exception as e:
        logger.error(traceback.format_exc())
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": f"获取机器人回复失败: {str(e)}"})


def process_video(video_path, audio_path, api_url="http://117.50.91.160:8000"):
    """
    处理视频和音频文件

    参数:
        video_path: 视频文件路径（MP4格式）
        audio_path: 音频文件路径（WAV格式）
        api_url: API服务器地址
    """
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
        if status_response.status_code == 502:
            continue
        status = status_response.json()
        print(f"当前状态: {status['status']}")

        if status['status'] == 'completed':
            # 3. 下载处理完成的视频
            print("处理完成，开始下载结果...")
            result_response = requests.get(f"{api_url}/result/{task_id}")

            if result_response.status_code == 200:
                output_filename = f"output_{task_id}_input.mp4"
                output_path = f"./uploads/download/output_{output_filename}"
                with open(output_path, 'wb') as f:
                    f.write(result_response.content)
                print(f"下载完成，保存到: {output_path}")
                return output_path
            else:
                print(f"下载失败: {result_response.text}")
                raise HTTPException(status_code=500, detail=f"获取机器人消息失败: {str(result_response.text)}")
            break

        elif status['status'] == 'failed':
            print(f"处理失败: {status.get('error', '未知错误')}")
            raise HTTPException(status_code=500, detail=f"获取机器人消息失败")
            break

        time.sleep(5)  # 每5秒检查一次状态



@app.post("/synthesize")
async def synthesize_video(text: str = Form(...), messages: str = Form(None)):
    """
    调用gpu_app合成视频
    
    参数:
        text: 用户输入的文本
        messages: 历史聊天记录（JSON字符串）
    """
    try:
        # 解析历史消息
        history_messages = []
        if messages:
            try:
                history_messages = json.loads(messages)
            except:
                pass
        rag_text = ''
        q_msg =''
        result_msg =[]
        if messages and len(history_messages)>1:
            q_msg = getds.get_messages_rag(messages)
            if q_msg!='关键词：无' and q_msg:
                q_msg = q_msg.replace('关键词：','')
                result_msg = vector_search(query=f"{q_msg}")
        if len(result_msg)>0:
            rag_text = result_msg[0].page_content
        # 根据历史聊天信息调用大模型生成机器人下一条对话
        prompt_str = messages + "上面是我们的聊天记录，聊天记录中我的标签是user，你的标签是bot，请明确区分你我的对话，不要把你的话当成我说的，你是一名懂健康养生的助手，我是顾客的角色，帮生成自然、对话式的回答,仅生成"
        chat_msg = getds.get_messages(history_messages,rag_text)
        robot_words = getds.get_response_qwen(chat_msg)
        #robot_words='你好，我是珍迪助手，请问有什么可以帮您吗'
        base_urlr = base_url + "/uploads/tts/"
        audio_path = ''
        APP_ID = '5f30a0b3'
        API_SECRET = 'MGYyMzJlYmYzZWVmMjIxZWE4ZThhNzA4'
        API_KEY = 'd4070941076c1e019907487878384f6c'

        file_path = './uploads/tts/'
        file_name = text_to_speech(robot_words, APP_ID, API_SECRET, API_KEY, file_path)

        # # 使用librosa加载音频文件
        # y, sr = librosa.load(file_path + file_name, sr=None)
        #
        # # 计算音频时长（秒）
        # duration = librosa.get_duration(y=y, sr=sr)
        #duration = round(duration)
        # 确保文件名不包含路径分隔符
        file_name = os.path.basename(file_name)
        file_path_url = base_urlr + file_name
        local_audio_path = file_path + file_name
        #----------------------
        # 定义一个字符串数组
        # my_list = ["tp4.mp4", "tp2.mp4", "tp3.mp4"]
        #
        # # 随机提取一个元素
        # random_item = random.choice(my_list)

        # video_path =f'./uploads/download/{random_item}'
        # aa = datetime.now()
        # video_path_combine = process_video(video_path, local_audio_path, api_url="http://117.50.91.160:8000")
        # bb =datetime.now()
        #
        # print('时间：'+str(bb-aa))
        # filename = os.path.basename(video_path_combine)
        # url_vedio = base_url+'/uploads/download/'+filename
        #-----------------------------

        time.sleep(2)
        url_vedio = r'http://localhost:8000\uploads\download\output_output_20250516_184534_input.mp4'#虚拟获取视频的方法后期加上

        #------------------------------

        return {"videoUrl": url_vedio,
                "text": robot_words
                }
    except Exception as e:
        logger.error(traceback.format_exc())
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"message": f"视频合成失败: {str(e)}"})

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)