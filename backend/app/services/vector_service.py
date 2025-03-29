import numpy as np
import json
import os
import uuid
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Union, Tuple

# LlamaIndex 相关导入
from llama_index.core import Document, VectorStoreIndex, load_index_from_storage
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.storage.storage_context import StorageContext
from llama_index.embeddings.siliconflow import SiliconFlowEmbedding
from llama_index.llms.siliconflow import SiliconFlow
from llama_index.vector_stores.faiss import FaissVectorStore

# 向量索引目录
VECTOR_DIR = Path("vector_indices")
VECTOR_DIR.mkdir(exist_ok=True)

# 索引存储目录
INDEX_STORE_DIR = Path("index_store")
INDEX_STORE_DIR.mkdir(exist_ok=True)

# 导入配置服务
from app.services.config_service import ConfigService

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_embedding_model():
    """获取嵌入模型"""
    if not ConfigService.is_llm_enabled():
        raise ValueError("LLM未启用，请在配置中启用LLM")
    
    llm_type = ConfigService.get_llm_type().lower()
    
    if llm_type == "siliconflow":
        # 使用SiliconFlow嵌入模型
        embed_config = ConfigService.get_embedding_config()
        
        embed_model = SiliconFlowEmbedding(
            model_name=embed_config["model_name"],
            api_base=embed_config["api_base"],
            api_key=embed_config["api_key"]
        )
        return embed_model
    
    # 可以根据需要添加其他类型的嵌入模型
    else:
        raise ValueError(f"不支持的LLM类型: {llm_type}")

def get_llm_model():
    """获取LLM模型"""
    if not ConfigService.is_llm_enabled():
        raise ValueError("LLM未启用，请在配置中启用LLM")
    
    llm_type = ConfigService.get_llm_type().lower()
    
    if llm_type == "siliconflow":
        # 使用SiliconFlow LLM模型
        completion_config = ConfigService.get_completion_config()
        
        llm = SiliconFlow(
            model_name=completion_config["model_name"],
            api_base=completion_config["api_base"],
            api_key=completion_config["api_key"],
            temperature=0.7,
            max_tokens=512
        )
        return llm
    
    # 可以根据需要添加其他类型的LLM模型
    else:
        raise ValueError(f"不支持的LLM类型: {llm_type}")

def create_vector_index(texts: List[str], file_id: str, use_llm: bool = False) -> str:
    """
    为文本创建向量索引
    
    Args:
        texts: 文本列表
        file_id: 原始文件ID
        use_llm: 是否使用LLM生成嵌入向量，默认为False
        
    Returns:
        索引ID
    """
    # 生成唯一的索引ID
    index_id = f"{file_id}_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 为当前索引创建专用目录
    index_store_path = INDEX_STORE_DIR / index_id
    if index_store_path.exists():
        shutil.rmtree(index_store_path)
    index_store_path.mkdir(exist_ok=True)
    
    # 索引元数据
    index_metadata = {
        "index_id": index_id,
        "file_id": file_id,
        "created_at": datetime.now().isoformat(),
        "texts": texts,
        "embedding_type": "llm" if use_llm else "tfidf"
    }
    
    try:
        if use_llm and ConfigService.is_llm_enabled():
            # 使用LlamaIndex创建文档对象
            documents = [Document(text=text) for text in texts]
            
            # 设置文本分块器
            parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=100)
            
            # 获取嵌入模型
            embed_model = get_embedding_model()
            
            # 创建FAISS向量存储
            import faiss
            dimension = 1024  # BGE-large-zh-v1.5的向量维度是1024
            faiss_index = faiss.IndexFlatL2(dimension)
            vector_store = FaissVectorStore(faiss_index=faiss_index)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # 创建向量索引
            index = VectorStoreIndex.from_documents(
                documents=documents,
                storage_context=storage_context,
                embed_model=embed_model,
                use_gpu=False
            )
            
            # 持久化索引
            index.storage_context.persist(persist_dir=str(index_store_path))
            
            # 更新元数据
            index_metadata["llm_type"] = ConfigService.get_llm_type().lower()
            embed_config = ConfigService.get_embedding_config()
            index_metadata["model"] = embed_config["model_name"]
            index_metadata["index_store_path"] = str(index_store_path)
            
            logger.info(f"使用LlamaIndex创建向量索引: {index_id}")
        else:
            # 如果不使用LLM，则使用原有的TF-IDF方法
            from sklearn.feature_extraction.text import TfidfVectorizer
            
            # 使用TF-IDF向量化文本
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # 将向量转换为可序列化的格式
            vectors = tfidf_matrix.toarray().tolist()
            
            # 更新索引元数据
            index_metadata["vectors"] = vectors
            index_metadata["vocabulary"] = vectorizer.vocabulary_
            index_metadata["idf"] = vectorizer.idf_.tolist()
            index_metadata["embedding_type"] = "tfidf"
            logger.info(f"使用TF-IDF创建向量索引: {index_id}")
    except Exception as e:
        logger.error(f"创建向量索引失败: {str(e)}")
        # 如果使用LLM失败，回退到TF-IDF
        if use_llm:
            logger.warning(f"LLM嵌入失败，回退到TF-IDF: {str(e)}")
            # 递归调用，但不使用LLM
            return create_vector_index(texts, file_id, use_llm=False)
        else:
            # 如果TF-IDF也失败，则抛出异常
            raise ValueError(f"创建向量索引失败: {str(e)}")
    
    # 保存元数据到文件
    index_file = VECTOR_DIR / f"{index_id}.json"
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index_metadata, f, ensure_ascii=False)
    
    return index_id

def search_vector_index(query: str, index_id: str, top_k: int = 5, rerank: bool = False) -> List[Dict[str, Any]]:
    """
    在向量索引中搜索相似内容
    
    Args:
        query: 查询文本
        index_id: 索引ID
        top_k: 返回的最相似结果数量
        rerank: 是否使用LLM重排序结果，仅当LLM启用时有效
        
    Returns:
        相似度最高的文本列表
    """
    # 读取索引文件
    index_file = VECTOR_DIR / f"{index_id}.json"
    with open(index_file, "r", encoding="utf-8") as f:
        index_data = json.load(f)
    
    embedding_type = index_data.get("embedding_type", "tfidf")
    results = []
    
    if embedding_type == "llm" and "index_store_path" in index_data:
        try:
            # 使用LlamaIndex加载索引
            index_store_path = index_data["index_store_path"]
            embed_model = get_embedding_model()
            
            # 从持久化存储加载索引
            storage_context = StorageContext.from_defaults(
                vector_store=FaissVectorStore.from_persist_dir(index_store_path),
                persist_dir=index_store_path
            )
            
            loaded_index = load_index_from_storage(
                storage_context=storage_context,
                embed_model=embed_model
            )
            
            # 创建检索器
            retriever = loaded_index.as_retriever(similarity_top_k=top_k)
            retrieved_nodes = retriever.retrieve(query)
            
            # 转换为结果格式
            for node in retrieved_nodes:
                results.append({
                    "text": node.node.text,
                    "similarity": float(node.score) if hasattr(node, 'score') else 0.0
                })
            
            logger.info(f"使用LlamaIndex搜索完成，找到{len(results)}个结果")
            
        except Exception as e:
            logger.warning(f"LlamaIndex搜索失败，回退到TF-IDF: {str(e)}")
            # 回退到TF-IDF搜索
            embedding_type = "tfidf"
    
    if embedding_type == "tfidf":
        # 使用原有的TF-IDF方法
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # 重建向量化器
        vectorizer = TfidfVectorizer(vocabulary=index_data["vocabulary"])
        # 手动设置IDF值
        vectorizer.idf_ = np.array(index_data["idf"])
        
        # 向量化查询
        query_vector = vectorizer.transform([query]).toarray()
        
        # 计算相似度
        similarities = cosine_similarity(query_vector, np.array(index_data["vectors"]))[0]
        
        # 获取相似度最高的结果
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "text": index_data["texts"][idx],
                "similarity": float(similarities[idx])
            })
        
        logger.info(f"使用TF-IDF搜索完成，找到{len(results)}个结果")
    
    # 使用LLM重排序结果
    if rerank and results and ConfigService.is_llm_enabled():
        try:
            reranked_results = rerank_results(query, results)
            logger.info("使用LLM重排序完成")
            return reranked_results
        except Exception as e:
            logger.warning(f"LLM重排序失败: {str(e)}")
    
    return results

def rerank_results(query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    使用LLM重排序搜索结果
    
    Args:
        query: 查询文本
        results: 初步搜索结果
        
    Returns:
        重排序后的结果
    """
    if not ConfigService.is_llm_enabled():
        return results
    
    try:
        # 获取LLM模型
        llm = get_llm_model()
        
        # 构建提示
        prompt = f"请评估以下文本片段与查询的相关性，并按照相关性从高到低排序。\n\n查询: {query}\n\n"
        print(prompt)
        for i, result in enumerate(results):
            prompt += f"[{i}] {result['text']}\n"
        
        # 使用LLM进行重排序
        response = llm.complete(prompt)
        reply = response.text
        
        # 尝试从回复中提取索引
        import re
        indices = re.findall(r'\[([0-9]+)\]', reply)
        indices = [int(idx) for idx in indices if idx.isdigit() and int(idx) < len(results)]
        
        # 如果成功提取到索引，则重排序结果
        if indices:
            reranked_results = [results[idx] for idx in indices]
            # 添加可能缺失的结果
            missing_indices = set(range(len(results))) - set(indices)
            for idx in missing_indices:
                reranked_results.append(results[idx])
            return reranked_results
        
    except Exception as e:
        logger.error(f"重排序请求失败: {str(e)}")
    
    # 如果重排序失败，返回原始结果
    return results

def semantic_search(query: str, index_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    使用LLM进行语义搜索，直接回答用户问题
    
    Args:
        query: 查询文本
        index_id: 索引ID
        top_k: 返回的最相似结果数量
        
    Returns:
        包含直接回答和相关文本片段的结果列表
    """
    # 首先使用向量搜索找到相关内容
    results = search_vector_index(query, index_id, top_k=top_k*2, rerank=True)
    
    if not results or not ConfigService.is_llm_enabled():
        return results[:top_k]
    
    try:
        # 读取索引文件获取索引存储路径
        index_file = VECTOR_DIR / f"{index_id}.json"
        with open(index_file, "r", encoding="utf-8") as f:
            index_data = json.load(f)
        
        if index_data.get("embedding_type") == "llm" and "index_store_path" in index_data:
            # 使用LlamaIndex的查询引擎
            index_store_path = index_data["index_store_path"]
            embed_model = get_embedding_model()
            llm = get_llm_model()
            
            # 从持久化存储加载索引
            storage_context = StorageContext.from_defaults(
                vector_store=FaissVectorStore.from_persist_dir(index_store_path),
                persist_dir=index_store_path
            )
            
            loaded_index = load_index_from_storage(
                storage_context=storage_context,
                embed_model=embed_model
            )
            
            # 创建查询引擎，配置更详细的响应模式
            query_engine = loaded_index.as_query_engine(
                llm=llm,
                response_mode="compact",  # 使用紧凑模式生成回答
                similarity_top_k=top_k,   # 控制检索的相关文档数量
                verbose=True              # 启用详细日志
            )
            
            print("执行语义查询：", query)
            # 执行查询
            response = query_engine.query(query)
            
            # 创建包含直接回答的结果
            direct_answer = {
                "answer": str(response),
                "is_direct_answer": True,
                "source_texts": []
            }
            
            # 添加相关文本作为来源
            semantic_results = [direct_answer]
            
            # 添加检索到的相关文本片段作为参考
            for result in results[:top_k]:
                direct_answer["source_texts"].append({
                    "text": result["text"],
                    "similarity": result["similarity"]
                })
            print("语义查询结果：", semantic_results)
            return semantic_results
        else:
            # 如果不是LlamaIndex索引，使用原有方法
            llm = get_llm_model()
            
            # 构建上下文
            context = "\n\n".join([f"文本片段 {i+1}: {result['text']}" for i, result in enumerate(results[:top_k])])
            
            # 构建更明确的提示，引导LLM生成直接回答
            prompt = f"""基于以下文本片段，直接回答用户的问题。

            {context}

            用户问题: {query}

            请提供一个完整、准确的回答。回答应该直接针对用户问题，而不是简单列出相关文本。如果文本片段中没有足够信息回答问题，请明确指出。

            回答:"""
            
            # 使用LLM生成回答
            response = llm.complete(prompt)
            reply = response.text
            
            # 创建包含直接回答的结果
            direct_answer = {
                "answer": reply,
                "is_direct_answer": True,
                "source_texts": []
            }
            
            # 添加相关文本作为来源
            semantic_results = [direct_answer]
            
            # 添加检索到的相关文本片段作为参考
            for result in results[:top_k]:
                direct_answer["source_texts"].append({
                    "text": result["text"],
                    "similarity": result["similarity"]
                })
            
            return semantic_results
    except Exception as e:
        logger.error(f"语义搜索请求失败: {str(e)}")
    
    # 如果语义搜索失败，返回原始结果
    return results[:top_k]
def semantic_search_multi(query: str, index_ids: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
    """
    在多个向量索引中进行语义搜索，直接回答用户问题
    
    Args:
        query: 查询文本
        index_ids: 索引ID列表
        top_k: 每个索引返回的最相似结果数量
        
    Returns:
        包含直接回答和相关文本片段的结果列表
    """
    if not index_ids:
        return []
    
    # 收集所有索引的搜索结果
    all_results = []
    for index_id in index_ids:
        try:
            # 验证索引是否存在
            index_file = VECTOR_DIR / f"{index_id}.json"
            if not index_file.exists():
                logger.warning(f"找不到向量索引: {index_id}")
                continue
            
            # 搜索单个索引
            results = search_vector_index(query, index_id, top_k=top_k, rerank=False)
            
            # 添加索引ID到结果中
            for result in results:
                result["index_id"] = index_id
            
            all_results.extend(results)
        except Exception as e:
            logger.error(f"搜索索引 {index_id} 失败: {str(e)}")
    
    if not all_results:
        return []
    
    # 按相似度排序所有结果
    all_results.sort(key=lambda x: x["similarity"], reverse=True)
    
    # 取前top_k个结果
    top_results = all_results[:top_k]
    
    # 如果启用了LLM，使用它生成直接回答
    if ConfigService.is_llm_enabled():
        try:
            # 获取LLM模型
            llm = get_llm_model()
            
            # 构建上下文
            context = "\n\n".join([f"文本片段 {i+1}: {result['text']}" for i, result in enumerate(top_results)])
            
            # 构建提示
            prompt = f"""基于以下文本片段，直接回答用户的问题。

            {context}

            用户问题: {query}

            请提供一个完整、准确的回答。回答应该直接针对用户问题，而不是简单列出相关文本。如果文本片段中没有足够信息回答问题，请明确指出。

            回答:"""
            
            # 使用LLM生成回答
            response = llm.complete(prompt)
            reply = response.text
            
            # 创建包含直接回答的结果
            direct_answer = {
                "answer": reply,
                "is_direct_answer": True,
                "source_texts": []
            }
            
            # 添加相关文本作为来源
            semantic_results = [direct_answer]
            
            # 添加检索到的相关文本片段作为参考
            for result in top_results:
                direct_answer["source_texts"].append({
                    "text": result["text"],
                    "similarity": result["similarity"],
                    "index_id": result.get("index_id", "")
                })
            
            return semantic_results
        except Exception as e:
            logger.error(f"多索引语义搜索请求失败: {str(e)}")
    
    # 如果语义搜索失败或LLM未启用，返回原始结果
    return top_results