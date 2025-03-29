import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

# 配置文件目录
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# 配置文件路径
CONFIG_FILE = DATA_DIR / "llm_config.json"

# 默认配置
DEFAULT_CONFIG = {
    "llm_type": "siliconflow",
    "openai": {
        "api_key": "",
        "api_base": "https://api.openai.com/v1",
        "embedding_model": "text-embedding-3-small",
        "completion_model": "gpt-3.5-turbo"
    },
    "huggingface": {
        "api_key": "",
        "api_base": "https://api-inference.huggingface.co/models",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
    },
    "siliconflow": {
        "api_key": "sk-tczexzwdkbzyuiakahqwamfzehhzpicrimxruftitatekjjn",
        "embedding_api_base": "https://api.siliconflow.cn/v1/embeddings",
        "completion_api_base": "https://api.siliconflow.cn/v1/chat/completions",
        "embedding_model": "BAAI/bge-large-zh-v1.5",
        "completion_model": "Qwen/QwQ-32B"
    }
}


class ConfigService:
    """配置服务类，用于管理LLM和嵌入模型的配置"""
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """获取配置信息"""
        if not CONFIG_FILE.exists():
            # 如果配置文件不存在，创建默认配置
            ConfigService.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config
        except Exception as e:
            print(f"读取配置文件失败: {str(e)}，使用默认配置")
            return DEFAULT_CONFIG
    
    @staticmethod
    def save_config(config: Dict[str, Any]) -> bool:
        """保存配置信息"""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")
            return False
    
    @staticmethod
    def update_config(config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新配置信息"""
        current_config = ConfigService.get_config()
        
        # 更新顶层配置
        for key, value in config_updates.items():
            if key in current_config and isinstance(value, dict) and isinstance(current_config[key], dict):
                # 如果是嵌套字典，递归更新
                current_config[key].update(value)
            else:
                # 否则直接替换
                current_config[key] = value
        
        # 保存更新后的配置
        ConfigService.save_config(current_config)
        return current_config
    
    @staticmethod
    def get_llm_type() -> str:
        """获取当前使用的LLM类型"""
        config = ConfigService.get_config()
        return config.get("llm_type", "siliconflow")
    
    @staticmethod
    def is_llm_enabled() -> bool:
        """检查是否启用了LLM"""
        llm_type = ConfigService.get_llm_type()
        return llm_type.lower() != "none"
    
    @staticmethod
    def get_embedding_config() -> Dict[str, Any]:
        """获取嵌入模型配置"""
        config = ConfigService.get_config()
        llm_type = config.get("llm_type", "siliconflow")
        
        if llm_type == "siliconflow":
            return {
                "model_name": config["siliconflow"]["embedding_model"],
                "api_base": config["siliconflow"]["embedding_api_base"],
                "api_key": config["siliconflow"]["api_key"]
            }
        elif llm_type == "openai":
            return {
                "model_name": config["openai"]["embedding_model"],
                "api_base": config["openai"]["api_base"],
                "api_key": config["openai"]["api_key"]
            }
        elif llm_type == "huggingface":
            return {
                "model_name": config["huggingface"]["embedding_model"],
                "api_base": config["huggingface"]["api_base"],
                "api_key": config["huggingface"]["api_key"]
            }
        else:
            raise ValueError(f"不支持的LLM类型: {llm_type}")
    
    @staticmethod
    def get_completion_config() -> Dict[str, Any]:
        """获取补全模型配置"""
        config = ConfigService.get_config()
        llm_type = config.get("llm_type", "siliconflow")
        
        if llm_type == "siliconflow":
            return {
                "model_name": config["siliconflow"]["completion_model"],
                "api_base": config["siliconflow"]["completion_api_base"],
                "api_key": config["siliconflow"]["api_key"]
            }
        elif llm_type == "openai":
            return {
                "model_name": config["openai"]["completion_model"],
                "api_base": config["openai"]["api_base"],
                "api_key": config["openai"]["api_key"]
            }
        else:
            raise ValueError(f"不支持的LLM类型: {llm_type}")