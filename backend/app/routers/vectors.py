from fastapi import APIRouter, HTTPException, Form, Body
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import os
import json
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.vector_service import create_vector_index, search_vector_index, semantic_search, semantic_search_multi

router = APIRouter(tags=["向量索引"])

# 上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 向量索引目录
VECTOR_DIR = Path("vector_indices")
VECTOR_DIR.mkdir(exist_ok=True)

@router.post("/create-index")
async def create_index(file_id: str = Form(...)):
    """根据选定的文本块创建向量索引"""
    try:
        # 验证选择文件是否存在
        selection_file = UPLOAD_DIR / f"selected_{file_id}.json"
        if not selection_file.exists():
            raise HTTPException(status_code=404, detail=f"找不到选择文件: {file_id}")
        
        # 读取选择的文本块
        with open(selection_file, "r", encoding="utf-8") as f:
            selected_chunks = json.load(f)
        
        if not selected_chunks:
            return JSONResponse(
                status_code=400,
                content={"message": "没有选择任何文本块"}
            )
        
        # 创建向量索引
        index_id = create_vector_index(selected_chunks, file_id, use_llm=True)
        
        return {
            "message": "向量索引创建成功",
            "index_id": index_id,
            "chunk_count": len(selected_chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建向量索引失败: {str(e)}")

@router.post("/search")
async def search_vectors(index_id: str = Form(...), query: str = Form(...), top_k: int = Form(5)):
    """在向量索引中搜索相似内容"""
    try:
        # 验证索引是否存在
        index_file = VECTOR_DIR / f"{index_id}.json"
        if not index_file.exists():
            raise HTTPException(status_code=404, detail=f"找不到向量索引: {index_id}")
        
        # 搜索向量
        results = semantic_search(query, index_id, top_k)
        
        return {
            "message": "搜索成功",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索向量失败: {str(e)}")

@router.get("/list-indices")
async def list_indices():
    """获取所有可用的向量索引"""
    try:
        indices = []
        
        # 遍历向量索引目录
        for index_file in VECTOR_DIR.glob("*.json"):
            try:
                # 读取索引文件
                with open(index_file, "r", encoding="utf-8") as f:
                    index_data = json.load(f)
                
                # 添加到结果列表
                indices.append(index_data)
            except Exception as e:
                # 跳过无法读取的索引文件
                continue
        
        return {
            "message": "获取索引列表成功",
            "indices": indices
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取索引列表失败: {str(e)}")

@router.post("/semantic-search-multi")
async def semantic_search_multiple(query: str = Form(...), index_ids: List[str] = Form(...), top_k: int = Form(5)):
    """在多个向量索引中搜索相似内容"""
    try:
        # 验证是否提供了索引ID
        if not index_ids:
            raise HTTPException(status_code=400, detail="未提供索引ID")
        
        # 验证索引是否存在
        for index_id in index_ids:
            index_file = VECTOR_DIR / f"{index_id}.json"
            if not index_file.exists():
                raise HTTPException(status_code=404, detail=f"找不到向量索引: {index_id}")
        
        # 搜索向量
        results = semantic_search_multi(query, index_ids, top_k)
        
        return {
            "message": "搜索成功",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索向量失败: {str(e)}")