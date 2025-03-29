# 文件处理与向量索引系统

这是一个前后端分离的项目，用于实现文件上传、数据清洗、文本拆分、向量索引和语义搜索功能。系统支持多种文件格式，并提供直观的用户界面进行操作。

## 功能特性

1. **文件上传与处理**
   - 支持上传CSV、Excel、TXT、Markdown、JSON等多种格式文件
   - 自动进行数据清洗和文本拆分
   - 可视化预览拆分后的文本块

2. **文本块选择与管理**
   - 交互式界面选择需要的文本块
   - 支持批量选择和取消选择
   - 实时预览选中的内容

3. **向量索引**
   - 基于选中的文本块创建向量索引
   - 支持多种向量模型（OpenAI、SiliconFlow、HuggingFace等）
   - 高效存储和检索向量数据

4. **语义搜索**
   - 基于向量相似度的语义搜索
   - 支持多索引联合搜索
   - 结果按相关性排序展示

5. **模型配置**
   - 灵活配置不同的LLM和Embedding模型
   - 支持多种AI服务提供商

## 技术栈

### 前端
- Vue 3 + Vite
- Pinia 状态管理
- Vue Router 路由管理

### 后端
- FastAPI 框架
- LlamaIndex 向量索引
- FAISS 向量存储
- 支持多种AI模型集成

## 部署指南

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 8+

### 后端部署

1. 克隆仓库并进入后端目录
   ```bash
   git clone <仓库地址>
   cd dataset/backend
   ```

2. 创建并激活虚拟环境（可选但推荐）
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/MacOS
   source venv/bin/activate
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 配置AI模型
   - 编辑 `backend/data/llm_config.json` 文件
   - 填入相应的API密钥和模型配置

5. 启动后端服务
   ```bash
   python run.py
   ```
   服务将在 http://localhost:8000 运行

### 前端部署

1. 进入前端目录
   ```bash
   cd dataset/frontend
   ```

2. 安装依赖
   ```bash
   npm install
   ```

3. 开发模式运行
   ```bash
   npm run dev
   ```
   开发服务器将在 http://localhost:5173 运行

4. 构建生产版本
   ```bash
   npm run build
   ```
   构建结果将保存在 `dist` 目录中

## 使用说明

1. 访问前端页面（开发模式下为 http://localhost:5173）
2. 在「数据集」页面上传文件并进行处理
3. 选择需要的文本块并创建向量索引
4. 在「向量搜索」页面进行语义搜索
5. 在「配置」页面可以调整模型设置

## 项目结构

```
./
├── frontend/         # 前端项目 (Vue 3 + Vite + Pinia)
│   ├── src/          # 源代码
│   │   ├── views/    # 页面组件
│   │   ├── stores/   # Pinia状态管理
│   │   └── router/   # 路由配置
└── backend/          # 后端项目 (FastAPI)
    ├── app/          # 应用代码
    │   ├── routers/  # API路由
    │   ├── services/ # 业务逻辑
    │   └── utils/    # 工具函数
    ├── data/         # 配置文件
    └── uploads/      # 上传文件存储
```