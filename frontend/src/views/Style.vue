<template>
  <div class="style-page">
    <div class="header">
      <router-link to="/" class="back-link">← 返回首页</router-link>
      <h1>风格模仿 & 润色</h1>
    </div>

    <div class="content-wrapper">
      <div class="panel input-panel">
        <h3>1. 输入原文本</h3>
        <textarea 
          v-model="originalText" 
          placeholder="请输入你需要改写的段落..."
          class="text-editor"
        ></textarea>

        <div class="controls">
          <div class="control-group">
            <label>目标风格</label>
            <div class="style-tags">
              <button 
                v-for="s in presetStyles" 
                :key="s"
                :class="['style-btn', { active: selectedStyle === s }]"
                @click="selectedStyle = s"
              >
                {{ s }}
              </button>
              <input 
                v-model="customStyle" 
                placeholder="自定义风格 (如：赛博朋克)" 
                class="custom-style-input"
                @focus="selectedStyle = ''"
              />
            </div>
          </div>

          <button @click="generateMimic" :disabled="loading" class="generate-btn">
            {{ loading ? "正在模仿中..." : "✨ 开始改写" }}
          </button>
        </div>
      </div>

      <div class="panel output-panel">
        <h3>2. 改写结果</h3>
        <div class="result-container">
          <textarea 
            v-model="resultText" 
            placeholder="AI 改写后的内容将显示在这里..."
            class="text-editor result-editor"
            readonly
          ></textarea>
          <button @click="copyResult" class="copy-btn" v-if="resultText">
            复制结果
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const originalText = ref('')
const resultText = ref('')
const loading = ref(false)
const selectedStyle = ref('金庸')
const customStyle = ref('')

const presetStyles = [
  '金庸 (武侠)', 
  '古龙 (冷峻)', 
  '鲁迅 (犀利)', 
  '张爱玲 (细腻)', 
  '王小波 (黑色幽默)',
  '翻译腔 (哦，我的上帝)',
  '网文爽文 (快节奏)',
  '克苏鲁 (不可名状)'
]

const targetStyle = computed(() => {
  return customStyle.value || selectedStyle.value || '正常'
})

async function generateMimic() {
  if (!originalText.value.trim()) {
    alert("请输入原文本")
    return
  }

  loading.value = true
  resultText.value = ''

  try {
    const provider = localStorage.getItem('novel_ai_provider')
    const model = localStorage.getItem('novel_ai_model')
    const apiKey = localStorage.getItem('novel_ai_api_key')
    const baseUrl = localStorage.getItem('novel_ai_base_url')

    const payload = {
      mode: 'mimic',
      context: {
        target_text: originalText.value,
        style: targetStyle.value
      },
      stream: true,
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
              resultText.value += data.content
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

function copyResult() {
  navigator.clipboard.writeText(resultText.value)
  alert("已复制到剪贴板")
}
</script>

<style scoped>
.style-page {
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
  min-height: 0;
}

.panel {
  flex: 1;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #eee;
  display: flex;
  flex-direction: column;
}

h3 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #333;
  font-size: 1.1em;
  border-bottom: 2px solid #673ab7;
  padding-bottom: 8px;
  display: inline-block;
}

.text-editor {
  flex: 1;
  width: 100%;
  resize: none;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 15px;
  font-size: 15px;
  line-height: 1.6;
  font-family: inherit;
  margin-bottom: 16px;
  transition: border-color 0.2s;
}

.text-editor:focus {
  border-color: #673ab7;
  outline: none;
}

.result-editor {
  background: #fafafa;
  border: none;
}

.controls {
  flex-shrink: 0;
}

.control-group {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #555;
  font-size: 0.9em;
}

.style-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.style-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9em;
  transition: all 0.2s;
  color: #555;
}

.style-btn.active {
  background: #673ab7;
  color: white;
  border-color: #673ab7;
}

.custom-style-input {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 20px;
  font-size: 0.9em;
  outline: none;
  width: 150px;
}

.custom-style-input:focus {
  border-color: #673ab7;
}

.generate-btn {
  width: 100%;
  padding: 12px;
  background: #673ab7;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: background 0.2s;
}

.generate-btn:hover:not(:disabled) {
  background: #5e35b1;
}

.generate-btn:disabled {
  background: #d1c4e9;
  cursor: not-allowed;
}

.result-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}

.copy-btn {
  position: absolute;
  bottom: 10px;
  right: 10px;
  padding: 6px 12px;
  background: rgba(0,0,0,0.6);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.copy-btn:hover {
  background: rgba(0,0,0,0.8);
}
</style>