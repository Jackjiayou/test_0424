from fastapi import FastAPI, HTTPException, Depends, Request, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import os
import json
import random
from datetime import datetime
import uuid
from  Ifasr_new import RequestApi
from  kdxf_tts_vtw import  vtw
import getds
import time

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

# 确保上传目录存在
os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/tts", exist_ok=True)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="."), name="static")
# 挂载上传目录，用于访问语音文件
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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
    1: [  # 新客户开发
        {
            "id": 1,
            "sceneId": 1,
            "text": "您好，我是客户李先生。听说贵公司有一些不错的产品，能简单介绍一下吗？",
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

# API路由

@app.get("/")
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
async def speech_to_text(audio_file: UploadFile = File(...), sceneId: int = Form(None), fileName: str = Form(None)):
    """
    将上传的语音文件转换为文本
    实际项目中应调用专业的语音识别API（如百度语音、讯飞语音等）
    
    此处为示例代码，真实实现时请替换为实际的语音识别API调用
    """
    # 使用传入的文件名或生成新的文件名
    if not fileName:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
        fileName = f"audio_{timestamp}_{random_str}.wav"
    
    # 确保文件名有正确的扩展名
    if not fileName.endswith(('.wav', '.mp3', '.aac')):
        fileName += '.wav'
    
    # 保存上传的文件
    file_location = f"uploads/{fileName}"
    os.makedirs("uploads", exist_ok=True)
    
    try:
        # 确保文件上传成功
        contents = await audio_file.read()
        with open(file_location, "wb") as f:
            f.write(contents)
        
        # 生成可访问的完整URL
        # 使用新的音频文件路由
        base_url = "http://0.0.0.0:8000"  # 开发环境
        # base_url = "https://your-production-domain.com"  # 生产环境
        voice_url = f"{base_url}/uploads/{fileName}"
        local_url = f"./uploads/{fileName}"
        # TODO: 此处调用您自己的语音识别API
        api = RequestApi(appid="5f30a0b3",
                         secret_key="dbfdebbd6299533f00fa97c6e8d1b008",
                         upload_file_path=local_url
                         )
        result = api.get_result()
        print(len(result))
        if len(result) == 0:
            print("receive result end")
        result1 = json.loads(result['content']['orderResult'])

        # 解析结果

        # 解析JSON数据
        # data = json.loads(result1['lattice'][0]['json_1best'])
        str_result = extract_words_from_lattice2(result1)
        
        return {"text":str_result , "voiceUrl": voice_url}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"上传文件处理失败: {str(e)}"}
        )

@app.post("/text-to-speech")
async def text_to_speech(text: str = Form(...)):
    """
    将文本转换为语音
    这里使用模拟数据，实际项目中应该调用语音合成API
    """
    # 模拟文字转语音的结果
    return {
        "voiceUrl": "/static/audio/response.mp3",
        "duration": str(random.randint(3, 10))
    }

@app.post("/analyze")
async def analyze_message(request: Dict[str, Any]):
    """
    分析用户消息并生成改进建议
    这里使用模拟数据，实际项目中应该调用大模型API
    """
    message = request.get("message", "")
    scene_id = request.get("sceneId", 1)
    
    # 随机选择一个建议模板
    suggestion = random.choice(suggestion_templates)
    
    return {
        "suggestion": suggestion,
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

@app.get("/generate-temp-audio")
async def generate_temp_audio(text: str = None):
    """
    生成临时语音文件
    实际项目中应该调用专业的语音合成API
    """
    # 生成唯一的文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
    fileName = f"temp_audio_{timestamp}_{random_str}.wav"
    
    # 确保文件名有正确的扩展名
    if not fileName.endswith(('.wav', '.mp3', '.aac')):
        fileName += '.wav'
    
    # 创建临时文件
    file_location = f"uploads/{fileName}"
    os.makedirs("uploads", exist_ok=True)
    
    try:
        # 创建一个简单的WAV文件
        # 这里我们创建一个1秒的静音WAV文件作为临时文件
        # 实际项目中应该调用语音合成API生成真实的语音文件
        with open(file_location, "wb") as f:
            # WAV文件头
            f.write(b'RIFF')
            f.write((36).to_bytes(4, byteorder='little'))  # 文件大小
            f.write(b'WAVE')
            f.write(b'fmt ')
            f.write((16).to_bytes(4, byteorder='little'))  # 格式块大小
            f.write((1).to_bytes(2, byteorder='little'))   # 音频格式 (1 = PCM)
            f.write((1).to_bytes(2, byteorder='little'))   # 通道数
            f.write((16000).to_bytes(4, byteorder='little'))  # 采样率
            f.write((32000).to_bytes(4, byteorder='little'))  # 字节率
            f.write((2).to_bytes(2, byteorder='little'))   # 块对齐
            f.write((16).to_bytes(2, byteorder='little'))  # 位深度
            f.write(b'data')
            f.write((0).to_bytes(4, byteorder='little'))   # 数据块大小
            
            # 生成1秒的静音数据 (16000Hz * 16bit * 1通道)
            for _ in range(16000):
                f.write((0).to_bytes(2, byteorder='little', signed=True))
        
        # 生成可访问的完整URL
        base_url = "http://0.0.0.0:8000"  # 开发环境
        # base_url = "https://your-production-domain.com"  # 生产环境
        voice_url = f"{base_url}/audio/{fileName}"
        
        return {"voiceUrl": voice_url, "duration": "1"}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"生成临时音频文件失败: {str(e)}"}
        )

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
async def get_robot_message(sceneId: int, messageCount: int, messages: Optional[str] = None):
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
    # 确保上传目录存在
    os.makedirs("./uploads/tts", exist_ok=True)
    
    # 设置基础URL，使用单斜杠
    base_url = "http://localhost:8000/uploads/tts/"
    
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
                file_name = vtw(text,file_path)
                # 确保文件名不包含路径分隔符
                file_name = os.path.basename(file_name)
                file_path_url = base_url+file_name
                duration = question["duration"]
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
                    prompt_str = messages+ "上面是我们的聊天记录，聊天记录中我的标签是user，你的标签是robot，我是一名大健康行业直销员，你是顾客的角色，通过对我提问和交流，对我不用太客气，有回答不满意的地方可以直说，锻炼我与客户沟通能力，请你结合历史聊天记录对我提问交流，仅输出下段话就可以"
                    robot_words = getds.get_response(prompt_str)


                    file_path = './uploads/tts/'
                    file_name = vtw(robot_words, file_path)
                    # 确保文件名不包含路径分隔符
                    file_name = os.path.basename(file_name)
                    file_path_url = base_url + file_name
                    duration = 5
                    return {
                        "text": robot_words,
                        "duration": duration,
                        "voiceUrl": file_path_url
                    }
                else:
                    # 如果最后一条是机器人消息，生成一个新的问题
                    scene_questions = questions.get(sceneId, [])
                    if scene_questions:
                        question = random.choice(scene_questions)
                        text = question["text"]
                        duration = question["duration"]
                    else:
                        text = f"在{scene_name}场景中，我们还需要考虑哪些因素？"
                        duration = "4"
            else:
                # 如果没有历史消息，生成一个默认问题
                text = f"在{scene_name}场景中，您认为最重要的是什么？"
                duration = "4"
        
        # 模拟语音合成
        # 在实际应用中，这里应该调用语音合成API
        # 这里我们使用预定义的语音URL
        scene_questions = questions.get(sceneId, [])
        voice_urls_for_scene = [q["voiceUrl"] for q in scene_questions]
        if voice_urls_for_scene:
            voice_url = random.choice(voice_urls_for_scene)
        else:
            # 默认语音URL
            voice_url = f"https://example.com/audio/default.mp3"
        
        # 返回结果
        return {
            "text": text,
            "duration": duration,
            "voiceUrl": voice_url
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取机器人消息失败: {str(e)}")

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 