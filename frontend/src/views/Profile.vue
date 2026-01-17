<template>
  <div class="profile-page">
    <div class="header">
      <router-link to="/" class="back-link">← 返回首页</router-link>
      <h1>个人中心</h1>
    </div>

    <div class="content-wrapper">
      <!-- 统计卡片 -->
      <div class="stats-section">
        <div class="stat-card">
          <div class="stat-value">{{ stats.novel_count || 0 }}</div>
          <div class="stat-label">作品数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.chapter_count || 0 }}</div>
          <div class="stat-label">总章节</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.word_count || 0 }}</div>
          <div class="stat-label">累计字数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.character_count || 0 }}</div>
          <div class="stat-label">创建角色</div>
        </div>
      </div>

      <div class="settings-section">
        <div class="panel">
          <h3>AI 设置</h3>
          
          <div class="form-group">
            <label>AI 提供商</label>
            <div class="provider-options">
              <label class="radio-label">
                <input type="radio" v-model="settings.provider" value="ollama">
                Ollama (本地运行)
              </label>
              <label class="radio-label">
                <input type="radio" v-model="settings.provider" value="openai_compat">
                OpenAI Compatible (DeepSeek / Claude 等云端 API)
              </label>
            </div>
          </div>

          <!-- Ollama 设置区域 -->
          <div v-if="settings.provider === 'ollama'" class="sub-settings">
            <div class="form-group">
              <label>选择模型</label>
              <div class="input-with-action">
                <select v-model="settings.model" class="form-select">
                  <option value="" disabled>-- 请选择模型 --</option>
                  <option v-for="m in ollamaModels" :key="m" :value="m">{{ m }}</option>
                </select>
                <button @click="fetchOllamaModels" :disabled="loadingModels" class="action-btn">
                  {{ loadingModels ? '刷新中...' : '刷新列表' }}
                </button>
              </div>
              <p class="hint" v-if="ollamaModels.length === 0">
                未检测到模型，请确保 Ollama 已启动 (默认 http://localhost:11434)
              </p>
            </div>
            <div class="form-group">
               <label>手动输入模型名 (如果列表为空)</label>
               <input v-model="settings.model" placeholder="例如: qwen2.5:7b" class="form-input" />
            </div>
          </div>

          <!-- OpenAI Compatible 设置区域 -->
          <div v-if="settings.provider === 'openai_compat'" class="sub-settings">
            <div class="form-group">
              <label>快速预设</label>
              <select v-model="selectedPreset" @change="applyPreset" class="form-select">
                <option v-for="p in providerPresets" :key="p.name" :value="p.name">
                  {{ p.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>API Key</label>
              <input 
                v-model="settings.apiKey" 
                type="password" 
                placeholder="sk-..." 
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label>API Base URL</label>
              <input 
                v-model="settings.baseUrl" 
                placeholder="https://api.example.com/v1" 
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label>模型名称</label>
              <input 
                v-model="settings.model" 
                placeholder="例如: deepseek-chat, gpt-4o" 
                class="form-input"
              />
            </div>
          </div>

          <div class="actions">
            <button @click="saveSettings" class="save-btn">保存设置</button>
            <span v-if="saveMessage" class="save-msg">{{ saveMessage }}</span>
          </div>
        </div>

        <div class="panel">
          <h3>关于</h3>
          <p>Novel AI 创作平台 v0.2.0</p>
          <p class="desc">一个基于 LLM 的辅助写作工具，旨在提供更流畅的创作体验。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { novelApi, aiApi } from '../api'

const stats = ref({})
const saveMessage = ref('')
const loadingModels = ref(false)
const ollamaModels = ref([])

const settings = ref({
  provider: localStorage.getItem('novel_ai_provider') || 'ollama',
  model: localStorage.getItem('novel_ai_model') || '',
  apiKey: localStorage.getItem('novel_ai_api_key') || '',
  baseUrl: localStorage.getItem('novel_ai_base_url') || ''
})

const providerPresets = [
  { name: 'DeepSeek', url: 'https://api.deepseek.com', defaultModel: 'deepseek-chat' },
  { name: 'Moonshot (Kimi)', url: 'https://api.moonshot.cn/v1', defaultModel: 'moonshot-v1-8k' },
  { name: 'Aliyun Bailian (通义)', url: 'https://dashscope.aliyuncs.com/compatible-mode/v1', defaultModel: 'qwen-plus' },
  { name: 'SiliconFlow (硅基流动)', url: 'https://api.siliconflow.cn/v1', defaultModel: 'deepseek-ai/DeepSeek-V3' },
  { name: 'OpenRouter', url: 'https://openrouter.ai/api/v1', defaultModel: 'deepseek/deepseek-chat' },
  { name: 'Custom (自定义)', url: '', defaultModel: '' }
]

const selectedPreset = ref('Custom (自定义)')

onMounted(async () => {
  await fetchStats()
  if (settings.value.provider === 'ollama') {
    fetchOllamaModels()
  }
  // Try to match current base URL to a preset
  const matched = providerPresets.find(p => p.url === settings.value.baseUrl)
  if (matched) {
    selectedPreset.value = matched.name
  }
})

async function fetchStats() {
  try {
    const res = await novelApi.getStats()
    stats.value = res.data || {}
  } catch (err) {
    console.error("获取统计失败", err)
  }
}

async function fetchOllamaModels() {
  loadingModels.value = true
  try {
    const res = await aiApi.listModels()
    if (res.data && Array.isArray(res.data)) {
      ollamaModels.value = res.data
      // If current model is not in list and list has items, select first one? 
      // Maybe not, user might have a custom one.
    }
  } catch (err) {
    console.error("获取 Ollama 模型失败", err)
  } finally {
    loadingModels.value = false
  }
}

function applyPreset() {
  const preset = providerPresets.find(p => p.name === selectedPreset.value)
  if (preset) {
    settings.value.baseUrl = preset.url
    if (preset.defaultModel) {
      settings.value.model = preset.defaultModel
    }
  }
}

function saveSettings() {
  localStorage.setItem('novel_ai_provider', settings.value.provider)
  localStorage.setItem('novel_ai_model', settings.value.model)
  localStorage.setItem('novel_ai_api_key', settings.value.apiKey)
  localStorage.setItem('novel_ai_base_url', settings.value.baseUrl)
  
  saveMessage.value = "设置已保存！"
  setTimeout(() => saveMessage.value = '', 3000)
}

// Watch provider change to auto-fetch models
watch(() => settings.value.provider, (newVal) => {
  if (newVal === 'ollama' && ollamaModels.value.length === 0) {
    fetchOllamaModels()
  }
})
</script>

<style scoped>
.profile-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.header {
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
  padding-bottom: 20px;
}

.back-link {
  text-decoration: none;
  color: #666;
  font-size: 14px;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #eee;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 8px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.panel {
  background: #f9f9f9;
  padding: 24px;
  border-radius: 8px;
  border: 1px solid #eee;
}

.panel h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.provider-options {
  display: flex;
  gap: 20px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.sub-settings {
  padding: 16px;
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 20px;
}

.form-select, .form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.input-with-action {
  display: flex;
  gap: 10px;
}

.action-btn {
  white-space: nowrap;
  padding: 0 16px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.action-btn:hover {
  background: #e0e0e0;
}

.hint {
  margin-top: 6px;
  font-size: 12px;
  color: #999;
}

.actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.save-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.save-btn:hover {
  background: #0056b3;
}

.save-msg {
  color: #28a745;
  font-size: 14px;
}
</style>