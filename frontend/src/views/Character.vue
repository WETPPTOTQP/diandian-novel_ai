<template>
  <div class="character-page">
    <div class="header">
      <router-link to="/" class="back-link">← 返回首页</router-link>
      <h1>人物生成器</h1>
    </div>

    <div class="content-wrapper">
      <div class="left-panel">
        <div class="section input-section">
          <h3>1. 生成设定</h3>
          <div class="form-group">
            <label>所属作品</label>
            <select v-model="selectedNovelId" @change="handleNovelChange" class="form-select">
              <option value="">-- 请选择作品 --</option>
              <option v-for="n in novels" :key="n.id" :value="n.id">{{ n.title }}</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>人物关键词 / 描述</label>
            <textarea 
              v-model="keywords" 
              placeholder="例如：反派，高智商，冷酷，悲惨童年，喜欢下棋..."
              rows="4"
            ></textarea>
          </div>
          
          <button @click="generateCharacter" :disabled="loading" class="generate-btn">
            {{ loading ? "AI 思考中..." : "✨ 生成人物档案" }}
          </button>
        </div>

        <div class="section result-section">
          <h3>2. 生成结果</h3>
          <div v-if="result" class="result-card">
            <textarea v-model="result" class="result-editor" rows="12"></textarea>
            
            <div class="save-actions" v-if="selectedNovelId">
              <input v-model="characterName" placeholder="输入角色姓名" class="name-input" />
              <button @click="saveCharacter" :disabled="saving" class="save-btn">
                {{ saving ? "保存中..." : "💾 保存到作品" }}
              </button>
            </div>
            <div v-else class="warning-text">
              请先选择作品以保存角色
            </div>
          </div>
          <div v-else class="placeholder">
            <p>生成的档案将显示在这里...</p>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="section list-section">
          <h3>已有人物 ({{ characters.length }})</h3>
          <div v-if="!selectedNovelId" class="empty-hint">请先选择作品查看人物</div>
          <div v-else-if="characters.length === 0" class="empty-hint">暂无人物档案</div>
          <div v-else class="character-list">
            <div v-for="char in characters" :key="char.id" class="character-item">
              <div class="char-header">
                <span class="char-name">{{ char.name }}</span>
                <button @click="deleteCharacter(char.id)" class="delete-btn">×</button>
              </div>
              <div class="char-profile">{{ char.profile }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { aiApi, novelApi } from '../api'

const novels = ref([])
const selectedNovelId = ref("")
const characters = ref([])

const keywords = ref('')
const loading = ref(false)
const result = ref('')

const characterName = ref('')
const saving = ref(false)

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
  characters.value = []
  if (!selectedNovelId.value) return
  
  try {
    const res = await novelApi.listCharacters(selectedNovelId.value)
    characters.value = res.data || []
  } catch (err) {
    console.error("加载人物列表失败", err)
  }
}

async function generateCharacter() {
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
      mode: 'character',
      context: {
        keywords: keywords.value
      },
      stream: true,
      novel_id: selectedNovelId.value,
      provider: provider || undefined,
      model: model || undefined,
      api_key: apiKey || undefined,
      base_url: baseUrl || undefined
    }

    // 使用原生 fetch 支持流式
    // 注意：这里需要导入 API_BASE，但 api/index.js 导出了吗？
    // 刚才我们修改 api/index.js 导出了 API_BASE
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
    
    // 尝试自动提取姓名 (简单规则：第一行包含"姓名："或类似)
    const nameMatch = result.value.match(/姓名[：:]\s*(\S+)/)
    if (nameMatch) {
      characterName.value = nameMatch[1]
    }

  } catch (err) {
    console.error(err)
    alert("生成失败: " + err.message)
  } finally {
    loading.value = false
  }
}

async function saveCharacter() {
  if (!selectedNovelId.value) {
    alert("请选择作品")
    return
  }
  if (!characterName.value.trim()) {
    alert("请输入角色姓名")
    return
  }
  if (!result.value.trim()) {
    alert("没有可保存的内容")
    return
  }

  saving.value = true
  try {
    await novelApi.createCharacter(selectedNovelId.value, {
      name: characterName.value,
      profile: result.value
    })
    // 刷新列表
    await handleNovelChange()
    // 清空输入
    characterName.value = ''
    result.value = ''
    keywords.value = ''
    alert("保存成功！")
  } catch (err) {
    alert("保存失败: " + err.message)
  } finally {
    saving.value = false
  }
}

async function deleteCharacter(id) {
  if (!confirm("确定删除这个人物吗？")) return
  try {
    await novelApi.deleteCharacter(id)
    await handleNovelChange()
  } catch (err) {
    alert("删除失败: " + err.message)
  }
}
</script>

<style scoped>
.character-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.header {
  margin-bottom: 24px;
  border-bottom: 1px solid #eee;
  padding-bottom: 16px;
}

.back-link {
  text-decoration: none;
  color: #666;
  font-size: 14px;
}

h1 {
  margin: 8px 0 0 0;
  font-size: 24px;
  color: #333;
}

.content-wrapper {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.right-panel {
  width: 350px;
  flex-shrink: 0;
}

.section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #eee;
}

.section h3 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
  color: #555;
  border-bottom: 2px solid #eee;
  padding-bottom: 8px;
}

.form-group {
  margin-bottom: 16px;
}

.form-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}

.generate-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: opacity 0.2s;
}

.generate-btn:hover {
  opacity: 0.9;
}

.generate-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.result-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.result-editor {
  width: 100%;
  border: none;
  padding: 16px;
  outline: none;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  min-height: 200px;
}

.save-actions {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: #f0f0f0;
  border-top: 1px solid #e0e0e0;
}

.name-input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.save-btn {
  padding: 8px 16px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn:hover {
  background: #059669;
}

.warning-text {
  padding: 10px;
  color: #f59e0b;
  font-size: 14px;
  text-align: center;
  background: #fffbeb;
}

.character-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 600px;
  overflow-y: auto;
}

.character-item {
  background: white;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #eee;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.char-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.char-name {
  font-weight: bold;
  color: #333;
}

.delete-btn {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  font-size: 16px;
  padding: 0 4px;
}

.delete-btn:hover {
  background: #fee2e2;
  border-radius: 4px;
}

.char-profile {
  font-size: 12px;
  color: #666;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.empty-hint {
  text-align: center;
  color: #999;
  padding: 20px 0;
}

.placeholder {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

@media (max-width: 768px) {
  .content-wrapper {
    flex-direction: column;
  }
  .right-panel {
    width: 100%;
  }
}
</style>
