import os
import shutil
from typing import Optional, Dict
import warnings
import logging
from datetime import datetime
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Disable albumentations version check warning
os.environ['ALBUMENTATIONS_DISABLE_VERSION_FLAG'] = '1'
warnings.filterwarnings('ignore', category=UserWarning)

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import torch
from omegaconf import OmegaConf
from diffusers import AutoencoderKL, DDIMScheduler
from latentsync.models.unet import UNet3DConditionModel
from latentsync.pipelines.lipsync_pipeline import LipsyncPipeline
from latentsync.whisper.audio2feature import Audio2Feature

# 配置日志
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 创建日志文件名（包含日期）
log_filename = os.path.join(LOG_DIR, f"latentsync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)
logger = logging.getLogger(__name__)

# 配置超时时间（秒）
TIMEOUT_UPLOAD = 300  # 上传文件超时时间
TIMEOUT_PROCESS = 1800  # 处理超时时间
TIMEOUT_DOWNLOAD = 300  # 下载结果超时时间

class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # 根据不同的端点设置不同的超时时间
        if request.url.path == "/process/":
            timeout = TIMEOUT_UPLOAD
        elif request.url.path.startswith("/result/"):
            timeout = TIMEOUT_DOWNLOAD
        else:
            timeout = 30  # 默认超时时间
            
        try:
            return await asyncio.wait_for(call_next(request), timeout=timeout)
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=504,
                content={"detail": f"Request timeout after {timeout} seconds"}
            )

app = FastAPI(title="LatentSync API", description="API for video lip-sync using LatentSync model")

# 添加超时中间件
app.add_middleware(TimeoutMiddleware)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# Global variables for model and pipeline
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

pipeline = None
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

# 存储任务状态
tasks_status: Dict[str, Dict] = {}

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_model():
    global pipeline
    if pipeline is not None:
        return
    
    try:
        logger.info("Starting model loading process...")
        
        # Load configs
        logger.info("Loading UNet configuration...")
        unet_config = OmegaConf.load("configs/unet/stage2.yaml")
        
        # Initialize models
        logger.info("Initializing noise scheduler...")
        noise_scheduler = DDIMScheduler.from_pretrained("configs")
        
        logger.info("Loading VAE model...")
        vae = AutoencoderKL.from_pretrained("stabilityai/sd-vae-ft-mse", torch_dtype=torch.float16)
        vae.config.scaling_factor = 0.18215
        vae.config.shift_factor = 0
        vae.requires_grad_(False)
        vae.to(device)
        
        # Load audio encoder based on cross attention dimension
        logger.info("Loading audio encoder...")
        if unet_config.model.cross_attention_dim == 768:
            whisper_model_path = "checkpoints/whisper/small.pt"
            logger.info("Using Whisper small model")
        elif unet_config.model.cross_attention_dim == 384:
            whisper_model_path = "checkpoints/whisper/tiny.pt"
            logger.info("Using Whisper tiny model")
        else:
            raise ValueError("cross_attention_dim must be 768 or 384")
            
        audio_encoder = Audio2Feature(
            model_path=whisper_model_path,
            device=device,
            num_frames=unet_config.data.num_frames,
            audio_feat_length=unet_config.data.audio_feat_length,
        )
        
        # Load UNet model
        logger.info("Loading UNet model...")
        denoising_unet, _ = UNet3DConditionModel.from_pretrained(
            OmegaConf.to_container(unet_config.model),
            "checkpoints/latentsync_unet.pt",
            device=device,
        )
        denoising_unet = denoising_unet.to(dtype=torch.float16)
        
        # Create pipeline
        logger.info("Creating LatentSync pipeline...")
        pipeline = LipsyncPipeline(
            vae=vae,
            audio_encoder=audio_encoder,
            denoising_unet=denoising_unet,
            scheduler=noise_scheduler,
        ).to(device)
        
        logger.info("Model loading completed successfully!")
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}", exc_info=True)
        raise RuntimeError(f"Failed to load model: {str(e)}")

async def process_video_task(
    task_id: str,
    video_path: str,
    audio_path: str,
    output_path: str,
    mask_path: str,
    inference_steps: int,
    guidance_scale: float
):
    try:
        tasks_status[task_id]["status"] = "processing"
        
        # Process video
        pipeline(
            video_path=video_path,
            audio_path=audio_path,
            video_out_path=output_path,
            video_mask_path=mask_path,
            num_frames=16,  # Default from config
            num_inference_steps=inference_steps,
            guidance_scale=guidance_scale,
            weight_dtype=torch.float16,
            width=256,  # Default from config
            height=256,  # Default from config
        )
        
        # Cleanup uploaded files
        os.remove(video_path)
        os.remove(audio_path)
        
        tasks_status[task_id]["status"] = "completed"
        tasks_status[task_id]["output_path"] = output_path
        
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {str(e)}", exc_info=True)
        tasks_status[task_id]["status"] = "failed"
        tasks_status[task_id]["error"] = str(e)
        # 清理文件
        for path in [video_path, audio_path, output_path, mask_path]:
            if os.path.exists(path):
                os.remove(path)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting LatentSync API server...")
    load_model()
    logger.info("Server startup completed!")

@app.post("/process/")
async def process_video(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    inference_steps: Optional[int] = 20,
    guidance_scale: Optional[float] = 2.0
):
    """
    Process a video with LatentSync model
    """
    try:
        task_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        logger.info(f"Received request {task_id}")
        logger.info(f"Parameters - inference_steps: {inference_steps}, guidance_scale: {guidance_scale}")
        logger.info(f"Input files - video: {video_file.filename}, audio: {audio_file.filename}")
        
        # Save uploaded files
        video_path = os.path.join(UPLOAD_DIR, f"{task_id}_{video_file.filename}")
        audio_path = os.path.join(UPLOAD_DIR, f"{task_id}_{audio_file.filename}")
        
        logger.info(f"Saving uploaded files to {UPLOAD_DIR}")
        with open(video_path, "wb") as f:
            shutil.copyfileobj(video_file.file, f)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio_file.file, f)
            
        # Generate output paths
        output_filename = f"output_{task_id}_{os.path.splitext(video_file.filename)[0]}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        mask_path = os.path.join(OUTPUT_DIR, f"mask_{output_filename}")
        
        # Initialize task status
        tasks_status[task_id] = {
            "status": "queued",
            "start_time": datetime.now().isoformat(),
            "output_path": None,
            "error": None
        }
        
        # Start processing in background
        background_tasks.add_task(
            process_video_task,
            task_id,
            video_path,
            audio_path,
            output_path,
            mask_path,
            inference_steps,
            guidance_scale
        )
        
        return JSONResponse({
            "task_id": task_id,
            "message": "Processing started",
            "status": "queued"
        })
        
    except Exception as e:
        logger.error(f"Error initiating request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """获取任务处理状态"""
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks_status[task_id]

@app.get("/result/{task_id}")
async def get_task_result(task_id: str):
    """获取处理完成的视频"""
    if task_id not in tasks_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = tasks_status[task_id]
    
    if task_info["status"] != "completed":
        return JSONResponse({
            "status": task_info["status"],
            "message": "Task is not completed yet" if task_info["status"] != "failed" else task_info["error"]
        })
    
    output_path = task_info["output_path"]
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=os.path.basename(output_path)
    )

@app.get("/health")
def health_check():
    """Check if the service is healthy"""
    status = {"status": "healthy", "model_loaded": pipeline is not None}
    logger.info(f"Health check - {status}")
    return status 