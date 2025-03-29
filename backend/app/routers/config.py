from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any
from app.services.config_service import ConfigService

router = APIRouter(tags=["配置管理"])

@router.get("/config")
async def get_config():
    """获取LLM和嵌入模型配置"""
    try:
        config = ConfigService.get_config()
        return {
            "message": "获取配置成功",
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")

@router.post("/config")
async def update_config(config_updates: Dict[str, Any] = Body(...)):
    """更新LLM和嵌入模型配置"""
    try:
        updated_config = ConfigService.update_config(config_updates)
        return {
            "message": "更新配置成功",
            "config": updated_config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")