<template>
    <div class="container">
        <!-- <h2>向量搜索</h2> -->
        <div class="vector-search-container">
            <!-- 左侧：向量索引列表 -->
            <div class="vector-indices-panel">
                <h3>可用向量索引</h3>
                <div v-if="isLoading" class="loading">
                    <div class="spinner"></div>
                    <p>加载中...</p>
                </div>
                <div v-else-if="error" class="error-message">
                    <p>{{ error }}</p>
                </div>
                <div v-else-if="indices.length === 0" class="empty-message">
                    <p>暂无可用的向量索引</p>
                </div>
                <div v-else class="indices-list">
                    <div v-for="index in indices" :key="index.index_id" class="index-item">
                        <label class="index-label">
                            <input type="checkbox" :value="index.index_id" v-model="selectedIndices">
                            <div class="index-info">
                                <div class="index-id">{{ index.index_id }}</div>
                                <div class="index-meta">
                                    <span>创建时间: {{ formatDate(index.created_at) }}</span>
                                    <span>文本块: {{ index.texts.length }}</span>
                                </div>
                            </div>
                        </label>
                    </div>
                </div>
            </div>

            <!-- 右侧：搜索面板 -->
            <div class="search-panel">
                <h3>向量搜索</h3>
                <div class="search-form">
                    <div class="form-group">
                        <label for="search-query">搜索查询:</label>
                        <input type="text" id="search-query" v-model="searchQuery" placeholder="输入搜索内容...">
                    </div>

                    <button class="primary-button" @click="searchVectors" :disabled="!canSearch || isSearching">
                        搜索
                    </button>
                </div>

                <div v-if="isSearching" class="loading">
                    <div class="spinner"></div>
                    <p>搜索中...</p>
                </div>

                <div v-if="searchResults.length > 0" class="search-results">
                    <h3>搜索结果:</h3>

                    <!-- 直接回答 -->
                    <div v-if="searchResults[0].is_direct_answer" class="direct-answer">
                        <h4>AI回答:</h4>
                        <p>{{ searchResults[0].answer }}</p>
                    </div>

                    <!-- 相关文本来源 -->
                    <div v-if="searchResults[0].source_texts && searchResults[0].source_texts.length > 0">
                        <h4>参考来源:</h4>
                        <div v-for="(source, index) in searchResults[0].source_texts" :key="index"
                            class="search-result">
                            <div class="result-header">
                                <span class="result-number">{{ index + 1 }}</span>
                                <span class="similarity">相似度: {{ (source.similarity * 100).toFixed(2) }}%</span>
                            </div>
                            <p>{{ source.text }}</p>
                        </div>
                    </div>

                    <!-- 传统搜索结果 (当没有直接回答时) -->
                    <div v-if="!searchResults[0].is_direct_answer">
                        <div v-for="(result, index) in searchResults" :key="index" class="search-result">
                            <div class="result-header">
                                <span class="result-number">{{ index + 1 }}</span>
                                <span class="similarity">相似度: {{ (result.similarity * 100).toFixed(2) }}%</span>
                            </div>
                            <p>{{ result.text }}</p>
                        </div>
                    </div>
                </div>

                <div v-else-if="hasSearched && !isSearching" class="empty-results">
                    <p>未找到匹配的结果</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// 状态变量
const indices = ref([])
const selectedIndices = ref([])
const searchQuery = ref('')
const searchResults = ref([])
const isLoading = ref(false)
const isSearching = ref(false)
const error = ref(null)
const hasSearched = ref(false)

// 计算属性
const canSearch = computed(() => {
    return searchQuery.value.trim() !== '' && selectedIndices.value.length > 0
})

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return ''
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
}

// 获取所有向量索引
async function fetchIndices() {
    isLoading.value = true
    error.value = null

    try {
        const response = await fetch('http://localhost:8000/api/list-indices')

        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || '获取向量索引失败')
        }

        const data = await response.json()
        indices.value = data.indices
    } catch (err) {
        error.value = err.message
        console.error('获取向量索引失败:', err)
    } finally {
        isLoading.value = false
    }
}

// 搜索向量
async function searchVectors() {
    if (!canSearch.value) return

    isSearching.value = true
    error.value = null
    hasSearched.value = true

    try {
        const formData = new FormData()
        formData.append('query', searchQuery.value)

        // 添加选中的索引ID
        selectedIndices.value.forEach(indexId => {
            formData.append('index_ids', indexId)
        })

        formData.append('top_k', 5) // 默认返回5个结果

        const response = await fetch('http://localhost:8000/api/semantic-search-multi', {
            method: 'POST',
            body: formData
        })

        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || '搜索向量失败')
        }

        const data = await response.json()
        searchResults.value = data.results
    } catch (err) {
        error.value = err.message
        console.error('搜索向量失败:', err)
    } finally {
        isSearching.value = false
    }
}

// 组件挂载时获取向量索引列表
onMounted(() => {
    fetchIndices()
})
</script>

<style scoped>
.container {
    padding: 20px;
}

.vector-search-container {
    display: flex;
    gap: 20px;
    margin-top: 20px;
}

.vector-indices-panel {
    flex: 1;
    background-color: #f5f5f5;
    border-radius: 8px;
    padding: 15px;
    max-width: 40%;
}

.search-panel {
    flex: 2;
    background-color: #f5f5f5;
    border-radius: 8px;
    padding: 15px;
}

.indices-list {
    max-height: 500px;
    overflow-y: auto;
}

.index-item {
    margin-bottom: 10px;
    background-color: white;
    border-radius: 4px;
    padding: 10px;
}

.index-label {
    display: flex;
    align-items: flex-start;
    cursor: pointer;
}

.index-info {
    margin-left: 10px;
    flex: 1;
}

.index-id {
    font-weight: bold;
    margin-bottom: 5px;
}

.index-meta {
    display: flex;
    flex-direction: column;
    font-size: 0.8rem;
    color: #666;
}

.search-form {
    display: flex;
    flex-direction: row;
    align-items: flex-end;
    gap: 10px;
    margin-bottom: 20px;
    flex-wrap: nowrap;
    width: 100%;
}

.form-group {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
}

.form-group input {
    width: 95%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.primary-button {
    background-color: #42b883;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    align-self: center;
}

.primary-button:disabled {
    background-color: #a8d5c2;
    cursor: not-allowed;
}

.loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px;
}

.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top: 4px solid #42b883;
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

.error-message {
    color: #e74c3c;
    padding: 10px;
    background-color: #fadbd8;
    border-radius: 4px;
    margin-bottom: 15px;
}

.empty-message,
.empty-results {
    text-align: center;
    padding: 20px;
    color: #7f8c8d;
}

.search-results {
    margin-top: 20px;
}

.direct-answer {
    background-color: #e8f5e9;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.search-result {
    background-color: white;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
}

.result-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}

.result-number {
    background-color: #42b883;
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
}

.similarity {
    font-size: 0.8rem;
    color: #7f8c8d;
}
</style>