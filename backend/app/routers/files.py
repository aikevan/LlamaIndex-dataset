from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
from app.services.file_processor import clean_data, split_text

router = APIRouter(tags=["文件处理"])

# 创建上传目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件并进行数据清洗和文本拆分"""
    try:
        # 保存上传的文件
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 根据文件类型进行处理
        file_ext = file.filename.split('.')[-1].lower()
        
        if file_ext in ['csv', 'xlsx', 'xls']:
            # 处理表格文件
            if file_ext == 'csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # 数据清洗
            cleaned_df = clean_data(df)
            
            # 文本拆分 (假设有一个文本列)
            text_columns = [col for col in cleaned_df.columns if cleaned_df[col].dtype == 'object']
            
            if not text_columns:
                return JSONResponse(
                    status_code=400,
                    content={"message": "未找到可拆分的文本列"}
                )
            
            # 选择第一个文本列进行拆分
            text_column = text_columns[0]
            split_results = []
            
            for idx, row in cleaned_df.iterrows():
                if pd.notna(row[text_column]):
                    text = str(row[text_column])
                    chunks = split_text(text)
                    split_results.append({
                        "row_id": idx,
                        "original_text": text,
                        "chunks": chunks
                    })
            
            # 保存处理结果
            result_file = UPLOAD_DIR / f"processed_{file.filename}.json"
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(split_results, f, ensure_ascii=False, indent=2)
            
            return {
                "message": "文件处理成功",
                "file_id": file.filename,
                "split_results": split_results
            }
            
        elif file_ext in ['txt', 'md', 'json']:
            # 处理文本文件
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            # 文本拆分
            chunks = split_text(text)
            
            split_results = [{
                "original_text": text,
                "chunks": chunks
            }]
            
            # 保存处理结果
            result_file = UPLOAD_DIR / f"processed_{file.filename}.json"
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(split_results, f, ensure_ascii=False, indent=2)
            
            return {
                "message": "文件处理成功",
                "file_id": file.filename,
                "split_results": split_results
            }
            
        else:
            return JSONResponse(
                status_code=400,
                content={"message": f"不支持的文件类型: {file_ext}"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")

@router.post("/select-chunks")
async def select_chunks(file_id: str = Form(...), selected_chunks: List[str] = Form(...)):
    """接收前端选择的文本块，准备进行向量索引"""
    try:
        # 验证文件是否存在
        result_file = UPLOAD_DIR / f"processed_{file_id}.json"
        if not result_file.exists():
            raise HTTPException(status_code=404, detail=f"找不到处理结果文件: {file_id}")
        
        # 分批处理文本块，每批最多1000个
        batch_size = 1000
        total_chunks = len(selected_chunks)
        processed_chunks = []
        
        for i in range(0, total_chunks, batch_size):
            batch = selected_chunks[i:i + batch_size]
            processed_chunks.extend(batch)
        
        # 保存选择的文本块
        selection_file = UPLOAD_DIR / f"selected_{file_id}.json"

        # 先读取现有内容（如果文件存在）
        try:
            with open(selection_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            existing_data = []

        # 确保现有数据是列表
        if not isinstance(existing_data, list):
            existing_data = [existing_data]

        # 追加新数据
        existing_data.extend(processed_chunks if isinstance(processed_chunks, list) else [processed_chunks])

        # 写入更新后的内容
        with open(selection_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        return {
            "message": "已接收选定的文本块",
            "file_id": file_id,
            "selected_count": len(processed_chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理选定文本块失败: {str(e)}")