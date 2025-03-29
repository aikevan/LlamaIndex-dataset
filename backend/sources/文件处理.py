# -*- coding: utf-8 -*-
# @Time    : 2023/10/21 10:55
# @Author  : liujx
# @FileName: 文件处理.py

import os
import logging
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.schema import Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore  # 注意类名变化
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core import VectorStoreIndex, load_index_from_storage

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义文件路径
file_path = os.path.join(os.path.dirname(__file__), "fengshenyanyi", "chapter_10.txt")
index_store_path = os.path.join(os.path.dirname(__file__), "fs_index_store")

try:

    import re

    def clean_text(text):
        # 去除HTML标签
        text = re.sub(r'<.*?>', '', text)
        
        # 去除广告和特殊字符（根据实际内容调整）
        text = re.sub(r'【.*?】|［.*?］|广告内容', '', text)
        
        # 合并多余的空格和换行符
        text = re.sub(r'\s+', ' ', text)
        
        # 处理特殊编码字符
        text = text.encode('utf-8', 'ignore').decode('utf-8')
        
        # 统一标点符号（可选）
        text = text.replace('“', '"').replace('”', '"')
        
        return text.strip()
    # 读取文件 txt
    # with open(file_path, "r", encoding="utf-8") as f:
    #     book_text = f.read()
    documents = SimpleDirectoryReader(input_files=[file_path],encoding="utf-8", errors='ignore').load_data()
    logger.info(f"成功读取文件: {file_path}")
    cleaned_documents = [Document(text=clean_text(doc.text)) for doc in documents]
    # cleaned_text = clean_text(book_text)
    logger.info(f"文本已清理")

    # 创建 LlamaIndex 文档对象
    # document = Document(text=cleaned_text)

    # 设置 chunk 大小（默认 512-1024 tokens）
    parser = SimpleNodeParser.from_defaults(chunk_size=1024, chunk_overlap=100)

    # 拆分文本
    nodes = parser.get_nodes_from_documents(cleaned_documents)
    logger.info(f"文本已拆分为 {len(nodes)} 个节点")

    # 初始化 embedding 模型 - 使用 SiliconFlow
    from llama_index.embeddings.siliconflow import SiliconFlowEmbedding
    
    # 配置 SiliconFlow API
    embed_model = SiliconFlowEmbedding(
        model_name="BAAI/bge-large-zh-v1.5",
        api_base="https://api.siliconflow.cn/v1/embeddings",
        api_key="sk-tczexzwdkbzyuiakahqwamfzehhzpicrimxruftitatekjjn"
    )
    
    # 创建 FAISS 向量存储 - 修复初始化方式
    import faiss
    
    faiss.omp_set_num_threads(4)
    # 创建一个空的 FAISS 索引
    dimension = 1024  # BGE-large-zh-v1.5 的向量维度是1024，不是1536
    faiss_index = faiss.IndexFlatL2(dimension)
    
    # 使用 FAISS 索引初始化向量存储
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # 使用 storage_context 创建索引
    index = VectorStoreIndex.from_documents(
        documents=cleaned_documents, 
        storage_context=storage_context,
        embed_model=embed_model,
        use_gpu=False
    )
    logger.info("向量索引已创建")

    # 使用SiliconFlow的LLM模型执行查询
    from llama_index.llms.siliconflow import SiliconFlow
    
    # # 配置SiliconFlow LLM
    sf_llm = SiliconFlow(
        model_name="Qwen/QwQ-32B",  # 或其他SiliconFlow支持的模型
        api_base="https://api.siliconflow.cn/v1/chat/completions",
        api_key="sk-tczexzwdkbzyuiakahqwamfzehhzpicrimxruftitatekjjn",
        temperature=0.7,
        max_tokens=512
    )
    
    # 使用SiliconFlow LLM创建查询引擎
    query_engine = index.as_query_engine(llm=sf_llm)
    
    response = query_engine.query("云中子是谁")
    print("首次查询结果:")
    print(response)

    # 持久化索引 - 修改持久化方式
    import pickle
    import shutil
    
    # 清理现有索引目录
    if os.path.exists(index_store_path):
        shutil.rmtree(index_store_path)
    os.makedirs(index_store_path)
    
    # 使用LlamaIndex的持久化方法
    index.storage_context.persist(persist_dir=index_store_path)
    logger.info("索引已使用LlamaIndex方式持久化")
    
    try:
        # 从持久化存储加载索引
        storage_context = StorageContext.from_defaults(
            vector_store=FaissVectorStore.from_persist_dir(index_store_path),
            persist_dir=index_store_path
        )
        
        loaded_index = load_index_from_storage(
            storage_context=storage_context,
            embed_model=embed_model
        )
        logger.info("已使用LlamaIndex方式加载索引")
        
        # 使用加载的索引执行查询
        loaded_query_engine = loaded_index.as_query_engine(llm=sf_llm)
        
        loaded_response = loaded_query_engine.query("云中子是谁")
        print("\n从持久化索引查询结果:")
        print(loaded_response)
        
        # 演示如何进行多次查询
        second_response = loaded_query_engine.query("小说中有哪些主要人物？")
        print("\n第二次查询结果:")
        print(second_response)
        
    except Exception as e:
        logger.error(f"加载索引时出错: {str(e)}")
        logger.error(f"错误类型: {type(e).__name__}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        # 尝试清理索引目录并重新创建
        logger.info("尝试重新创建索引...")
        import shutil
        if os.path.exists(index_store_path):
            shutil.rmtree(index_store_path)
            os.makedirs(index_store_path)
        
        # 使用二进制模式保存索引
        index.storage_context.persist(persist_dir=index_store_path)
        logger.info("索引已重新创建")
    except Exception as e:
        logger.error(f"加载索引时出错: {e}")

except FileNotFoundError:
    logger.error(f"文件未找到: {file_path}")
except Exception as e:
    logger.error(f"处理过程中出错: {str(e)}")