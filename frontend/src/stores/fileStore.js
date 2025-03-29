import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useFileStore = defineStore('file', () => {
    // 状态
    const isLoading = ref(false)
    const error = ref(null)
    const fileId = ref(null)
    const splitResults = ref([])
    const selectedChunks = ref([])
    const indexId = ref(null)
    const indexCreated = ref(false)
    const searchResults = ref([])

    // 计算属性
    const hasSelectedChunks = computed(() => selectedChunks.value.length > 0)
    const canCreateIndex = computed(() => hasSelectedChunks.value && fileId.value && !indexCreated.value)

    // 上传文件
    async function uploadFile(file) {
        isLoading.value = true
        error.value = null

        try {
            const formData = new FormData()
            formData.append('file', file)

            const response = await fetch('http://localhost:8000/api/upload', {
                method: 'POST',
                body: formData
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || '上传文件失败')
            }

            const data = await response.json()
            fileId.value = data.file_id
            splitResults.value = data.split_results
            return data
        } catch (err) {
            error.value = err.message
            throw err
        } finally {
            isLoading.value = false
        }
    }

    // 提交选择的文本块
    async function submitSelectedChunks() {
        if (!hasSelectedChunks.value || !fileId.value) return

        isLoading.value = true
        error.value = null

        try {
            // 分批处理，每批最多1000个文本块
            const BATCH_SIZE = 500
            const chunks = [...selectedChunks.value]
            const totalChunks = chunks.length
            let processedCount = 0
            let lastResponse = null

            // 处理每一批次
            for (let i = 0; i < totalChunks; i += BATCH_SIZE) {
                const batchChunks = chunks.slice(i, i + BATCH_SIZE)
                const formData = new FormData()
                formData.append('file_id', fileId.value)

                // 添加当前批次的文本块
                batchChunks.forEach(chunk => {
                    formData.append('selected_chunks', chunk)
                })

                const response = await fetch('http://localhost:8000/api/select-chunks', {
                    method: 'POST',
                    body: formData
                })

                if (!response.ok) {
                    const errorData = await response.json()
                    throw new Error(errorData.detail || `提交第${i / BATCH_SIZE + 1}批文本块失败`)
                }

                lastResponse = await response.json()
                processedCount += batchChunks.length
            }

            return {
                ...lastResponse,
                message: `已成功提交所有文本块，共${processedCount}个`,
                total_processed: processedCount
            }
        } catch (err) {
            error.value = err.message
            throw err
        } finally {
            isLoading.value = false
        }
    }

    // 创建向量索引
    async function createIndex() {
        if (!canCreateIndex.value) return

        isLoading.value = true
        error.value = null

        try {
            const formData = new FormData()
            formData.append('file_id', fileId.value)

            const response = await fetch('http://localhost:8000/api/create-index', {
                method: 'POST',
                body: formData
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || '创建向量索引失败')
            }

            const data = await response.json()
            indexId.value = data.index_id
            indexCreated.value = true
            return data
        } catch (err) {
            error.value = err.message
            throw err
        } finally {
            isLoading.value = false
        }
    }

    // 搜索向量
    async function searchVectors(query) {
        if (!indexId.value || !query) return

        isLoading.value = true
        error.value = null

        try {
            const formData = new FormData()
            formData.append('index_id', indexId.value)
            formData.append('query', query)
            formData.append('top_k', 5) // 默认返回5个结果

            const response = await fetch('http://localhost:8000/api/search', {
                method: 'POST',
                body: formData
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || '搜索向量失败')
            }

            const data = await response.json()
            searchResults.value = data.results
            return data
        } catch (err) {
            error.value = err.message
            throw err
        } finally {
            isLoading.value = false
        }
    }

    // 重置状态
    function reset() {
        fileId.value = null
        splitResults.value = []
        selectedChunks.value = []
        indexId.value = null
        indexCreated.value = false
        searchResults.value = []
        error.value = null
    }

    return {
        // 状态
        isLoading,
        error,
        fileId,
        splitResults,
        selectedChunks,
        indexId,
        indexCreated,
        searchResults,

        // 计算属性
        hasSelectedChunks,
        canCreateIndex,

        // 方法
        uploadFile,
        submitSelectedChunks,
        createIndex,
        searchVectors,
        reset
    }
})