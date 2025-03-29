from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import files, vectors, config

app = FastAPI(
    title="文件处理与向量索引API",
    description="提供文件上传、数据清洗、文本拆分和向量索引功能的API",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置为具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(files.router, prefix="/api")
app.include_router(vectors.router, prefix="/api")
app.include_router(config.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "文件处理与向量索引API服务正在运行"}