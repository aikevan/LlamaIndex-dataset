<template>
    <div class="container">
        <main>
            <!-- 步骤导航 -->
            <div class="steps">
                <div class="step" :class="{ active: currentStep >= 1 }">
                    <div class="step-number">1</div>
                    <div class="step-text">上传文件</div>
                </div>
                <div class="step" :class="{ active: currentStep >= 2 }">
                    <div class="step-number">2</div>
                    <div class="step-text">选择文本块</div>
                </div>
                <div class="step" :class="{ active: currentStep >= 3 }">
                    <div class="step-number">3</div>
                    <div class="step-text">创建向量索引</div>
                </div>
                <div class="step" :class="{ active: currentStep >= 4 }">
                    <div class="step-number">4</div>
                    <div class="step-text">向量搜索</div>
                </div>
            </div>

            <!-- 加载指示器 -->
            <div v-if="fileStore.isLoading" class="loading">
                <div class="spinner"></div>
                <p>处理中，请稍候...</p>
            </div>

            <!-- 错误提示 -->
            <div v-if="fileStore.error" class="error-message">
                <p>{{ fileStore.error }}</p>
                <button @click="fileStore.error = null">关闭</button>
            </div>

            <!-- 步骤1: 文件上传 -->
            <div v-if="currentStep === 1" class="step-content">
                <h2>上传文件</h2>
                <p>支持的文件类型: CSV, Excel, TXT, Markdown, JSON</p>

                <div class="file-upload" style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <label for="file-input" class="file-label">
                            <span>选择文件</span>
                            <input type="file" id="file-input" @change="handleFileChange"
                                accept=".csv,.xlsx,.xls,.txt,.md,.json">
                        </label>
                        <span v-if="selectedFile">已选择: {{ selectedFile.name }}</span>
                    </div>
                    <button class="primary-button" @click="uploadFile" :disabled="!selectedFile || fileStore.isLoading">
                        上传并处理
                    </button>
                </div>
            </div>

            <!-- 步骤2: 选择文本块 -->
            <div v-if="currentStep === 2" class="step-content">
                <h2>选择文本块</h2>
                <p>从下面的文本块中选择需要进行向量索引的内容</p>

                <!-- 全选功能 -->
                <div class="select-all-container" style="margin-bottom: 15px;">
                    <label class="select-all-label" style="display: flex; align-items: center; cursor: pointer;">
                        <input type="checkbox" v-model="selectAll" @change="toggleSelectAll">
                        <span style="margin-left: 8px; font-weight: bold;">全选</span>
                    </label>
                </div>

                <div class="text-chunks">
                    <div v-for="(result, resultIndex) in fileStore.splitResults" :key="resultIndex"
                        class="result-group">
                        <h3 v-if="fileStore.splitResults.length > 1">文本组 {{ resultIndex + 1 }}</h3>

                        <!-- <div class="original-text">
                            <h4>原始文本:</h4>
                            <p>{{ result.original_text }}</p>
                        </div> -->

                        <h4>拆分后的文本块:</h4>
                        <div v-for="(chunk, chunkIndex) in result.chunks" :key="chunkIndex" class="chunk">
                            <label class="chunk-label">
                                <input type="checkbox" :value="chunk" v-model="selectedChunksSet"
                                    @change="updateSelectedChunks">
                                <div class="chunk-content">
                                    <span class="chunk-number">{{ chunkIndex + 1 }}</span>
                                    <p>{{ chunk }}</p>
                                </div>
                            </label>
                        </div>
                    </div>
                </div>

                <div class="step-actions">
                    <button class="secondary-button" @click="currentStep = 1">返回</button>
                    <button class="primary-button" @click="submitSelectedChunks"
                        :disabled="!fileStore.hasSelectedChunks || fileStore.isLoading">
                        提交选择 ({{ fileStore.selectedChunks.length }})
                    </button>
                </div>
            </div>

            <!-- 步骤3: 创建向量索引 -->
            <div v-if="currentStep === 3" class="step-content">
                <h2>创建向量索引</h2>
                <p>为选定的{{ fileStore.selectedChunks.length }}个文本块创建向量索引</p>

                <div class="selected-summary">
                    <h3>已选择的文本块:</h3>
                    <ul>
                        <li v-for="(chunk, index) in fileStore.selectedChunks.slice(0, 3)" :key="index">
                            {{ chunk.substring(0, 100) }}{{ chunk.length > 100 ? '...' : '' }}
                        </li>
                        <li v-if="fileStore.selectedChunks.length > 3">
                            ...还有{{ fileStore.selectedChunks.length - 3 }}个文本块
                        </li>
                    </ul>
                </div>

                <div v-if="fileStore.indexCreated" class="success-message">
                    <p>向量索引创建成功! 索引ID: {{ fileStore.indexId }}</p>
                </div>

                <div class="step-actions">
                    <button class="secondary-button" @click="currentStep = 2">返回</button>
                    <button class="primary-button" @click="createIndex"
                        :disabled="!fileStore.canCreateIndex || fileStore.isLoading">
                        创建向量索引
                    </button>
                    <button v-if="fileStore.indexCreated" class="primary-button" @click="currentStep = 4">
                        继续到向量搜索
                    </button>
                </div>
            </div>

            <!-- 步骤4: 向量搜索 -->
            <div v-if="currentStep === 4" class="step-content">
                <h2>向量搜索</h2>
                <p>在创建的向量索引中搜索相似内容</p>

                <div class="search-form">
                    <div class="form-group">
                        <label for="search-query">搜索查询:</label>
                        <input type="text" id="search-query" v-model="searchQuery" placeholder="输入搜索内容...">
                    </div>

                    <button class="primary-button" @click="searchVectors"
                        :disabled="!searchQuery || fileStore.isLoading">
                        搜索
                    </button>
                </div>

                <div v-if="fileStore.searchResults.length > 0" class="search-results">
                    <h3>搜索结果:</h3>

                    <!-- 直接回答 -->
                    <div v-if="fileStore.searchResults[0].is_direct_answer" class="direct-answer">
                        <h4>AI回答:</h4>
                        <p>{{ fileStore.searchResults[0].answer }}</p>
                    </div>

                    <!-- 相关文本来源 -->
                    <div
                        v-if="fileStore.searchResults[0].source_texts && fileStore.searchResults[0].source_texts.length > 0">
                        <h4>参考来源:</h4>
                        <div v-for="(source, index) in fileStore.searchResults[0].source_texts" :key="index"
                            class="search-result">
                            <div class="result-header">
                                <span class="result-number">{{ index + 1 }}</span>
                                <span class="similarity">相似度: {{ (source.similarity * 100).toFixed(2) }}%</span>
                            </div>
                            <p>{{ source.text }}</p>
                        </div>
                    </div>

                    <!-- 传统搜索结果 (当没有直接回答时) -->
                    <div v-if="!fileStore.searchResults[0].is_direct_answer">
                        <div v-for="(result, index) in fileStore.searchResults" :key="index" class="search-result">
                            <div class="result-header">
                                <span class="result-number">{{ index + 1 }}</span>
                                <span class="similarity">相似度: {{ (result.similarity * 100).toFixed(2) }}%</span>
                            </div>
                            <p>{{ result.text }}</p>
                        </div>
                    </div>
                </div>

                <div class="step-actions">
                    <button class="secondary-button" @click="currentStep = 3">返回</button>
                    <button class="secondary-button" @click="resetProcess">重新开始</button>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useFileStore } from '../stores/fileStore'

// 初始化Pinia store
const fileStore = useFileStore()

// 状态变量
const currentStep = ref(1)
const selectedFile = ref(null)
const searchQuery = ref('')
const selectedChunksSet = ref(new Set())
const selectAll = ref(false)

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
    // 检查是否所有文本块都被选中，更新全选状态
    updateSelectAllState()
}

// 更新全选状态
function updateSelectAllState() {
    // 获取所有可选的文本块
    const allChunks = getAllChunks()
    // 如果所有文本块都被选中，则全选状态为true，否则为false
    selectAll.value = allChunks.length > 0 && allChunks.every(chunk => selectedChunksSet.value.has(chunk))
}

// 获取所有可选的文本块
function getAllChunks() {
    const allChunks = []
    fileStore.splitResults.forEach(result => {
        result.chunks.forEach(chunk => {
            allChunks.push(chunk)
        })
    })
    return allChunks
}

// 全选/取消全选
function toggleSelectAll() {
    const allChunks = getAllChunks()

    if (selectAll.value) {
        // 全选
        allChunks.forEach(chunk => {
            selectedChunksSet.value.add(chunk)
        })
    } else {
        // 取消全选
        selectedChunksSet.value.clear()
    }

    // 更新选择的文本块
    updateSelectedChunks()
}

// 创建向量索引
async function createIndex() {
    if (!fileStore.canCreateIndex) return

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
    currentStep.value = 1
    selectedFile.value = null
    searchQuery.value = ''
    selectedChunksSet.value = new Set()
    fileStore.reset()
}

// 组件挂载时检查是否有索引ID
onMounted(() => {
    // 如果有索引ID，直接跳到搜索步骤
    if (fileStore.indexId) {
        currentStep.value = 4
    }
})

// 提交选择的文本块
async function submitSelectedChunks() {
    if (!fileStore.hasSelectedChunks) return

    // 确保selectedChunks已经更新
    updateSelectedChunks()

    try {
        // 先调用store的submitSelectedChunks方法
        await fileStore.submitSelectedChunks()
        // 成功后再进入下一步
        currentStep.value = 3
    } catch (error) {
        console.error('提交选中的文本块失败:', error)
    }
}
</script>

<style scoped>
/* 组件样式保持与原App.vue相同 */
</style>