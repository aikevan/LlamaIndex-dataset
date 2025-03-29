<template>
    <div class="container">
        <header>
            <div class="header-content">
                <h1 class="site-title">资料库</h1>
                <nav class="main-nav">
                    <router-link to="/" class="nav-link">首页</router-link>
                    <router-link to="/dataset" class="nav-link">数据处理</router-link>
                    <router-link to="/vector-search" class="nav-link">向量搜索</router-link>
                    <router-link to="/config" class="nav-link">配置</router-link>
                </nav>
            </div>
        </header>

        <main>
            <router-view></router-view>
        </main>

        <footer>
            <p>资料库 &copy; 2023</p>
        </footer>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useFileStore } from './stores/fileStore'

// App.vue只负责布局和导航
const fileStore = useFileStore()

// 状态变量
const currentStep = ref(1)
const selectedFile = ref(null)
const searchQuery = ref('')
const selectedChunksSet = ref(new Set())

// 处理文件选择
function handleFileChange(event) {
    const file = event.target.files[0]
    if (file) {
        selectedFile.value = file
    }
}

// 上传文件
async function uploadFile() {
    if (!selectedFile.value) return

    try {
        await fileStore.uploadFile(selectedFile.value)
        currentStep.value = 2
    } catch (error) {
        console.error('上传文件失败:', error)
    }
}

// 更新选择的文本块
function updateSelectedChunks() {
    fileStore.selectedChunks = Array.from(selectedChunksSet.value)
}

// 提交选择的文本块
async function submitSelectedChunks() {
    try {
        await fileStore.submitSelectedChunks()
        currentStep.value = 3
    } catch (error) {
        console.error('提交选择的文本块失败:', error)
    }
}

// 创建向量索引
async function createIndex() {
    try {
        await fileStore.createIndex()
    } catch (error) {
        console.error('创建向量索引失败:', error)
    }
}

// 搜索向量
async function searchVectors() {
    if (!searchQuery.value) return

    try {
        await fileStore.searchVectors(searchQuery.value)
    } catch (error) {
        console.error('搜索向量失败:', error)
    }
}

// 重置流程
function resetProcess() {
    fileStore.reset()
    currentStep.value = 1
    selectedFile.value = null
    searchQuery.value = ''
    selectedChunksSet.value = new Set()
}
</script>

<style>
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: Arial, sans-serif;
}

header {
    background-color: #42b883;
    color: white;
    padding: 15px 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.main-nav {
    display: flex;
}

.nav-link {
    color: white;
    text-decoration: none;
    padding: 8px 15px;
    margin: 0 10px;
    border-radius: 4px;
    transition: background-color 0.3s;
}

.nav-link:hover {
    background-color: rgba(255, 255, 255, 0.2);
}

.router-link-active {
    background-color: rgba(255, 255, 255, 0.3);
    font-weight: bold;
}

header h1.site-title {
    color: white;
    font-size: 1.5rem;
    margin: 0;
}

/* 步骤导航 */
.steps {
    display: flex;
    justify-content: space-between;
    margin-bottom: 30px;
    position: relative;
}

.steps::before {
    content: '';
    position: absolute;
    top: 20px;
    left: 0;
    right: 0;
    height: 2px;
    background-color: #e0e0e0;
    z-index: -1;
}

.step {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 120px;
}

.step-number {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #e0e0e0;
    color: #fff;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: bold;
    margin-bottom: 10px;
}

.step.active .step-number {
    background-color: #42b883;
}

.step-text {
    text-align: center;
    font-size: 14px;
    color: #666;
}

.step.active .step-text {
    color: #42b883;
    font-weight: bold;
}

/* 加载指示器 */
.loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 20px 0;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top-color: #42b883;
    animation: spin 1s ease-in-out infinite;
    margin-bottom: 10px;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* 错误消息 */
.error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.error-message button {
    background-color: transparent;
    border: none;
    color: #721c24;
    cursor: pointer;
    font-weight: bold;
}

/* 成功消息 */
.success-message {
    background-color: #d4edda;
    color: #155724;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 20px;
}

/* 步骤内容 */
.step-content {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 30px;
}

.step-content h2 {
    margin-top: 0;
    color: #2c3e50;
    margin-bottom: 15px;
}

/* 文件上传 */
.file-upload {
    margin: 20px 0;
    display: flex;
    align-items: center;
}

.file-label {
    display: inline-block;
    padding: 10px 20px;
    background-color: #42b883;
    color: white;
    border-radius: 4px;
    cursor: pointer;
    margin-right: 15px;
}

.file-label:hover {
    background-color: #3aa876;
}

input[type="file"] {
    display: none;
}

/* 按钮样式 */
.primary-button {
    background-color: #42b883;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
}

.primary-button:hover {
    background-color: #3aa876;
}

.primary-button:disabled {
    background-color: #a0d5c2;
    cursor: not-allowed;
}

.secondary-button {
    background-color: #6c757d;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    margin-right: 10px;
}

.secondary-button:hover {
    background-color: #5a6268;
}

/* 文本块选择 */
.text-chunks {
    max-height: 500px;
    overflow-y: auto;
    margin: 20px 0;
}

.result-group {
    margin-bottom: 30px;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 20px;
}

.original-text {
    background-color: #e8f4f8;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 20px;
}

.chunk {
    margin-bottom: 10px;
}

.chunk-label {
    display: flex;
    align-items: flex-start;
    cursor: pointer;
}

.chunk-content {
    margin-left: 10px;
    flex-grow: 1;
    background-color: white;
    padding: 10px;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
}

.chunk-number {
    display: inline-block;
    width: 24px;
    height: 24px;
    background-color: #6c757d;
    color: white;
    border-radius: 50%;
    text-align: center;
    line-height: 24px;
    margin-right: 10px;
}

/* 步骤操作 */
.step-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
}

/* 搜索表单 */
.search-form {
    margin: 20px 0;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.form-group input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
}

/* 搜索结果 */
.search-results {
    margin-top: 30px;
}

.direct-answer {
    background-color: #e8f5e9;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 20px;
    border: 1px solid #c8e6c9;
}

.direct-answer h4 {
    color: #2e7d32;
    margin-top: 0;
    margin-bottom: 10px;
}

.search-result {
    background-color: white;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 15px;
    border: 1px solid #e0e0e0;
}

.result-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 1px solid #eee;
}

.result-number {
    display: inline-block;
    width: 24px;
    height: 24px;
    background-color: #42b883;
    color: white;
    border-radius: 50%;
    text-align: center;
    line-height: 24px;
}

.similarity {
    color: #6c757d;
    font-weight: bold;
}

/* 选择摘要 */
.selected-summary {
    background-color: #f0f0f0;
    padding: 15px;
    border-radius: 4px;
    margin: 20px 0;
}

.selected-summary ul {
    margin: 10px 0;
    padding-left: 20px;
}

.selected-summary li {
    margin-bottom: 5px;
}

footer {
    text-align: center;
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid #e0e0e0;
    color: #6c757d;
}
</style>
