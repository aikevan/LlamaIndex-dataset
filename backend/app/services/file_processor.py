import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    对数据进行清洗处理
    
    Args:
        df: 输入的DataFrame数据
        
    Returns:
        清洗后的DataFrame
    """
    # 复制数据，避免修改原始数据
    cleaned_df = df.copy()
    
    # 处理缺失值
    for col in cleaned_df.columns:
        # 对数值列使用均值填充
        if pd.api.types.is_numeric_dtype(cleaned_df[col]):
            cleaned_df[col].fillna(cleaned_df[col].mean(), inplace=True)
        # 对分类列使用众数填充
        elif pd.api.types.is_categorical_dtype(cleaned_df[col]):
            cleaned_df[col].fillna(cleaned_df[col].mode()[0], inplace=True)
        # 对文本列使用空字符串填充
        elif pd.api.types.is_string_dtype(cleaned_df[col]) or cleaned_df[col].dtype == 'object':
            cleaned_df[col].fillna('', inplace=True)
    
    # 删除重复行
    cleaned_df.drop_duplicates(inplace=True)
    
    # 处理异常值（针对数值列，使用3倍标准差法）
    for col in cleaned_df.columns:
        if pd.api.types.is_numeric_dtype(cleaned_df[col]):
            mean = cleaned_df[col].mean()
            std = cleaned_df[col].std()
            # 将超出3倍标准差的值替换为均值
            cleaned_df.loc[cleaned_df[col] > mean + 3*std, col] = mean
            cleaned_df.loc[cleaned_df[col] < mean - 3*std, col] = mean
    
    return cleaned_df

def split_text(text: str, max_chunk_size: int = 512, overlap: int = 100) -> List[str]:
    """
    将文本拆分成多个块
    
    Args:
        text: 输入文本
        max_chunk_size: 每个块的最大字符数
        overlap: 块之间的重叠字符数
        
    Returns:
        拆分后的文本块列表
    """
    # 如果文本为空或长度小于最大块大小，直接返回
    if not text or len(text) <= max_chunk_size:
        return [text] if text else []
    
    # 按句子拆分文本
    sentences = re.split(r'(?<=[。！？.!?])', text)
    sentences = [s for s in sentences if s.strip()]
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # 如果当前句子加上当前块的长度小于最大块大小，则添加到当前块
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += sentence
        else:
            # 如果当前块不为空，添加到结果中
            if current_chunk:
                chunks.append(current_chunk)
            
            # 如果单个句子超过最大块大小，需要进一步拆分
            if len(sentence) > max_chunk_size:
                # 按字符拆分
                for i in range(0, len(sentence), max_chunk_size - overlap):
                    chunk = sentence[i:i + max_chunk_size]
                    chunks.append(chunk)
                current_chunk = sentence[-overlap:] if overlap > 0 else ""
            else:
                current_chunk = sentence
    
    # 添加最后一个块
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks