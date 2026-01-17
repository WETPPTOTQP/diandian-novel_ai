<template>
  <div class="ideas-page">
    <div class="header">
      <router-link to="/" class="back-link">← 返回首页</router-link>
      <h1>灵感构思 & 脑暴</h1>
    </div>

    <div class="content-wrapper">
      <!-- 左侧：输入与生成 -->
      <div class="left-panel">
        <div class="section input-section">
          <h3>1. 构思设定</h3>
          
          <div class="form-group">
            <label>所属作品 (提供上下文)</label>
            <select v-model="selectedNovelId" @change="handleNovelChange" class="form-select">
              <option value="">-- 不关联作品 (通用灵感) --</option>
              <option v-for="n in novels" :key="n.id" :value="n.id">{{ n.title }}</option>
            </select>
          </div>

          <div class="form-group">
            <label>灵感类型</label>
            <div class="type-selector">
              <button 
                v-for="type in ideaTypes" 
                :key="type.value"
                :class="['type-btn', { active: ideaType === type.value }]"
                @click="ideaType = type.value"
              >
                {{ type.label }}
              </button>
            </div>
          </div>
          
          <div class="form-group">
            <label>关键词 / 核心点 / 困惑</label>
            <textarea 
              v-model="keywords" 
              :placeholder="currentPlaceholder"
              rows="4"
            ></textarea>
          </div>
          
          <button @click="generateIdea" :disabled="loading" class="generate-btn">
            {{ loading ? "AI 正在燃烧脑细胞..." : "✨ 开始构思" }}
          </button>
        </div>

        <div class="section result-section">
          <h3>2. 构思结果</h3>
          <div class="result-card">
            <textarea v-model="result" class="result-editor" rows="12" placeholder="AI 的奇思妙想将出现在这里..."></textarea>
            
            <div class="save-actions" v-if="selectedNovelId && result">
              <button @click="saveIdea" :disabled="saving" class="save-btn">
                {{ saving ? "保存中..." : "💾 保存灵感" }}
              </button>
            </div>
            <div v-else-if="result" class="warning-text">
              选择作品后可保存灵感
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：灵感列表 -->
      <div class="right-panel">
        <div class="section list-section">
          <h3>灵感记录 ({{ ideas.length }})</h3>
          <div v-if="!selectedNovelId" class="empty-hint">选择作品以查看历史灵感</div>
          <div v-else-if="ideas.length === 0" class="empty-hint">暂无灵感记录</div>
          <div v-else class="idea-list">
            <div v-for="idea in ideas" :key="idea.id" class="idea-item">
              <div class="idea-header">
                <span class="idea-type-tag">{{ getTypeName(idea.idea_type) }}</span>
                <span class="idea-date">{{ formatDate(idea.created_at) }}</span>
                <button @click="deleteIdea(idea.id)" class="delete-btn">×</button>
              </div>
              <div class="idea-content">{{ idea.content }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { aiApi, novelApi } from '../api'

const novels = ref([])
const selectedNovelId = ref("")
const ideas = ref([])

const keywords = ref('')
const loading = ref(false)
const result = ref('')
const saving = ref(false)

const ideaType = ref('outline')
const ideaTypes = [
  { value: 'outline', label: '故事大纲', placeholder: '输入故事核心梗概、类型、主要人物...' },
  { value: 'plot_twist', label: '情节转折', placeholder: '输入当前剧情卡点、需要反转的情节...' },
  { value: 'story_fragment', label: '脑洞片段', placeholder: '输入画面感关键词、特定场景氛围...' },
  { value: 'world_building', label: '世界观', placeholder: '输入地理环境、力量体系、社会规则...' }
]

const currentPlaceholder = computed(() => {
  const type = ideaTypes.find(t => t.value === ideaType.value)
  return type ? type.placeholder : '请输入关键词...'
})

onMounted(async () => {
  await loadNovels()
})

async function loadNovels() {
  try {
    const res = await novelApi.listNovels()
    novels.value = res.data || []
  } catch (err) {
    console.error("加载作品列表失败", err)
  }
}

async function handleNovelChange() {
  ideas.value = []
  if (!selectedNovelId.value) return
  
  try {
    const res = await novelApi.listIdeas(selectedNovelId.value)
    ideas.value = res.data || []
  } catch (err) {
    console.error("加载灵感列表失败", err)
  }
}

function getTypeName(typeVal) {
  const t = ideaTypes.find(it => it.value === typeVal)
  return t ? t.label : typeVal
}

function formatDate(isoStr) {
  return new Date(isoStr).toLocaleString()
}

async function generateIdea() {
  if (!keywords.value.trim()) {
    alert("请输入一些关键词")
    return
  }

  loading.value = true
  result.value = ''
  
  try {
    const provider = localStorage.getItem('novel_ai_provider')
    const model = localStorage.getItem('novel_ai_model')
    const apiKey = localStorage.getItem('novel_ai_api_key')
    const baseUrl = localStorage.getItem('novel_ai_base_url')

    const payload = {
      mode: ideaType.value,
      context: {
        keywords: keywords.value
      },
      stream: true,
      novel_id: selectedNovelId.value || undefined,
      provider: provider || undefined,
      model: model || undefined,
      api_key: apiKey || undefined,
      base_url: baseUrl || undefined
    }

    const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:5000"
    const response = await fetch(`${API_BASE}/api/ai/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) throw new Error("API请求失败")

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ""

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ""

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6)
          if (dataStr === '[DONE]') continue
          try {
            const data = JSON.parse(dataStr)
            if (data.content) {
              result.value += data.content
            }
          } catch (e) {
            console.error(e)
          }
        }
      }
    }
  } catch (err) {
    console.error(err)
    alert("生成失败: " + err.message)
  } finally {
    loading.value = false
  }
}

async function saveIdea() {
  if (!selectedNovelId.value) return
  if (!result.value.trim()) return

  saving.value = true
  try {
    await novelApi.createIdea(selectedNovelId.value, {
      content: result.value,
      idea_type: ideaType.value
    })
    // 刷新列表
    await handleNovelChange()
    alert("保存成功！")
  } catch (err) {
    console.error(err)
    alert("保存失败: " + err.message)
  } finally {
    saving.value = false
  }
}

async function deleteIdea(id) {
  if (!confirm("确定删除这条灵感吗？")) return
  try {
    await novelApi.deleteIdea(id)
    await handleNovelChange()
  } catch (err) {
    console.error(err)
    alert("删除失败")
  }
}
</script>

<style scoped>
.ideas-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  margin-bottom: 20px;
  flex-shrink: 0;
}

.back-link {
  text-decoration: none;
  color: #666;
  font-size: 14px;
}

.content-wrapper {
  display: flex;
  gap: 24px;
  flex: 1;
  min-height: 0; /* Important for scrolling */
}

.left-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
}

.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 300px;
}

.section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #eee;
}

.input-section {
  flex-shrink: 0;
}

.result-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.list-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f9f9f9;
}

h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #333;
  font-size: 1.1em;
  border-bottom: 2px solid #e91e63;
  padding-bottom: 8px;
  display: inline-block;
}

.form-group {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #555;
  font-size: 0.9em;
}

.form-select, textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-family: inherit;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-select:focus, textarea:focus {
  border-color: #e91e63;
  outline: none;
}

.type-selector {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.type-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9em;
  transition: all 0.2s;
}

.type-btn.active {
  background: #e91e63;
  color: white;
  border-color: #e91e63;
}

.generate-btn {
  width: 100%;
  padding: 12px;
  background: #e91e63;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: background 0.2s;
}

.generate-btn:hover:not(:disabled) {
  background: #d81b60;
}

.generate-btn:disabled {
  background: #ffb4c9;
  cursor: not-allowed;
}

.result-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  min-height: 0;
}

.result-editor {
  flex: 1;
  width: 100%;
  resize: none;
  border: none;
  background: #fafafa;
  padding: 15px;
  border-radius: 6px;
  font-size: 15px;
  line-height: 1.6;
  color: #333;
}

.save-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.save-btn {
  padding: 8px 20px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.warning-text {
  margin-top: 10px;
  color: #999;
  font-size: 0.9em;
  text-align: right;
}

.idea-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 5px;
}

.idea-item {
  background: white;
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
  transition: transform 0.2s;
}

.idea-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.idea-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 0.85em;
  color: #888;
}

.idea-type-tag {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  color: #555;
}

.delete-btn {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 16px;
  padding: 0 4px;
}

.delete-btn:hover {
  color: #f44336;
}

.idea-content {
  font-size: 14px;
  color: #444;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  white-space: pre-wrap;
}

.empty-hint {
  text-align: center;
  color: #999;
  margin-top: 40px;
  font-style: italic;
}
</style>