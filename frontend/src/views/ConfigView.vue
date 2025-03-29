<template>
    <div class="config-container">
        <h1>模型配置</h1>
        <p class="description">配置LLM和嵌入模型相关信息</p>

        <div v-if="isLoading" class="loading">
            <div class="spinner"></div>
            <p>加载中，请稍候...</p>
        </div>

        <div v-if="error" class="error-message">
            <p>{{ error }}</p>
            <button @click="error = null">关闭</button>
        </div>

        <form @submit.prevent="saveConfig" class="config-form">
            <!-- LLM类型选择 -->
            <div class="form-group">
                <label for="llm-type">LLM类型:</label>
                <select id="llm-type" v-model="config.llm_type" class="form-control">
                    <option value="siliconflow">SiliconFlow</option>
                    <option value="openai">OpenAI</option>
                    <option value="huggingface">HuggingFace</option>
                    <option value="none">不使用LLM</option>
                </select>
            </div>

            <!-- SiliconFlow配置 -->
            <div v-if="config.llm_type === 'siliconflow'" class="config-section">
                <h2>SiliconFlow配置</h2>

                <div class="form-group">
                    <label for="sf-api-key">API密钥:</label>
                    <input type="password" id="sf-api-key" v-model="config.siliconflow.api_key" class="form-control">
                </div>

                <div class="form-group">
                    <label for="sf-embedding-api-base">嵌入API地址:</label>
                    <input type="text" id="sf-embedding-api-base" v-model="config.siliconflow.embedding_api_base"
                        class="form-control">
                </div>

                <div class="form-group">
                    <label for="sf-completion-api-base">补全API地址:</label>
                    <input type="text" id="sf-completion-api-base" v-model="config.siliconflow.completion_api_base"
                        class="form-control">
                </div>

                <div class="form-group">
                    <label for="sf-embedding-model">嵌入模型:</label>
                    <input type="text" id="sf-embedding-model" v-model="config.siliconflow.embedding_model"
                        class="form-control">
                </div>

                <div class="form-group">
                    <label for="sf-completion-model">补全模型:</label>
                    <input type="text" id="sf-completion-model" v-model="config.siliconflow.completion_model"
                        class="form-control">
                </div>
            </div>

            <!-- OpenAI配置 -->
            <div v-if="config.llm_type === 'openai'" class="config-section">
                <h2>OpenAI配置</h2>

                <div class="form-group">
                    <label for="openai-api-key">API密钥:</label>
                    <input type="password" id="openai-api-key" v-model="config.openai.api_key" class="form-control">
                </div>

                <div class="form-group">
                    <label for="openai-api-base">API地址:</label>
                    <input type="text" id="openai-api-base" v-model="config.openai.api_base" class="form-control">
                </div>

                <div class="form-group">
                    <label for="openai-embedding-model">嵌入模型:</label>
                    <input type="text" id="openai-embedding-model" v-model="config.openai.embedding_model"
                        class="form-control">
                </div>

                <div class="form-group">
                    <label for="openai-completion-model">补全模型:</label>
                    <input type="text" id="openai-completion-model" v-model="config.openai.completion_model"
                        class="form-control">
                </div>
            </div>

            <!-- HuggingFace配置 -->
            <div v-if="config.llm_type === 'huggingface'" class="config-section">
                <h2>HuggingFace配置</h2>

                <div class="form-group">
                    <label for="hf-api-key">API密钥:</label>
                    <input type="password" id="hf-api-key" v-model="config.huggingface.api_key" class="form-control">
                </div>

                <div class="form-group">
                    <label for="hf-api-base">API地址:</label>
                    <input type="text" id="hf-api-base" v-model="config.huggingface.api_base" class="form-control">
                </div>

                <div class="form-group">
                    <label for="hf-embedding-model">嵌入模型:</label>
                    <input type="text" id="hf-embedding-model" v-model="config.huggingface.embedding_model"
                        class="form-control">
                </div>
            </div>

            <div class="form-actions">
                <button type="submit" class="primary-button" :disabled="isLoading">保存配置</button>
                <button type="button" class="secondary-button" @click="resetConfig" :disabled="isLoading">重置</button>
            </div>
        </form>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

// 状态变量
const isLoading = ref(false)
const error = ref(null)
const config = reactive({
    llm_type: 'siliconflow',
    openai: {
        api_key: '',
        api_base: 'https://api.openai.com/v1',
        embedding_model: 'text-embedding-3-small',
        completion_model: 'gpt-3.5-turbo'
    },
    huggingface: {
        api_key: '',
        api_base: 'https://api-inference.huggingface.co/models',
        embedding_model: 'sentence-transformers/all-MiniLM-L6-v2'
    },
    siliconflow: {
        api_key: '',
        embedding_api_base: 'https://api.siliconflow.cn/v1/embeddings',
        completion_api_base: 'https://api.siliconflow.cn/v1/chat/completions',
        embedding_model: 'BAAI/bge-large-zh-v1.5',
        completion_model: 'Qwen/QwQ-32B'
    }
})

// 获取配置
async function fetchConfig() {
    isLoading.value = true
    error.value = null

    try {
        const response = await fetch('http://localhost:8000/api/config')

        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || '获取配置失败')
        }

        const data = await response.json()

        // 更新配置
        Object.assign(config, data.config)
    } catch (err) {
        error.value = err.message
        console.error('获取配置失败:', err)
    } finally {
        isLoading.value = false
    }
}

// 保存配置
async function saveConfig() {
    isLoading.value = true
    error.value = null

    try {
        const response = await fetch('http://localhost:8000/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        })

        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || '保存配置失败')
        }

        const data = await response.json()
        alert('配置保存成功')
    } catch (err) {
        error.value = err.message
        console.error('保存配置失败:', err)
    } finally {
        isLoading.value = false
    }
}

// 重置配置
function resetConfig() {
    fetchConfig()
}

// 组件挂载时获取配置
onMounted(() => {
    fetchConfig()
})
</script>

<style scoped>
.config-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.description {
    color: #666;
    margin-bottom: 20px;
}

.config-form {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.config-section {
    margin-top: 20px;
    padding: 15px;
    background-color: #fff;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.form-group {
    margin-bottom: 15px;
}

label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
}

.form-control {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

select.form-control {
    height: 38px;
}

.form-actions {
    margin-top: 30px;
    display: flex;
    gap: 10px;
}

.primary-button {
    background-color: #42b883;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.primary-button:hover {
    background-color: #3aa876;
}

.primary-button:disabled {
    background-color: #a8d5c3;
    cursor: not-allowed;
}

.secondary-button {
    background-color: #e0e0e0;
    color: #333;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.secondary-button:hover {
    background-color: #d0d0d0;
}

.secondary-button:disabled {
    background-color: #f0f0f0;
    color: #999;
    cursor: not-allowed;
}

.loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 20px 0;
}

.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top: 4px solid #42b883;
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
    margin-bottom: 10px;
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
    background-color: #ffebee;
    color: #c62828;
    padding: 10px 15px;
    border-radius: 4px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.error-message button {
    background-color: transparent;
    border: none;
    color: #c62828;
    cursor: pointer;
    font-weight: bold;
}
</style>