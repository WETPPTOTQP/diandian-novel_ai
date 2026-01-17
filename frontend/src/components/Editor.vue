<template>
  <div class="editor-container">
    <div v-if="editor" class="editor-toolbar">
      <button @click="editor.chain().focus().toggleBold().run()" :class="{ 'is-active': editor.isActive('bold') }">
        Bold
      </button>
      <button @click="editor.chain().focus().toggleItalic().run()" :class="{ 'is-active': editor.isActive('italic') }">
        Italic
      </button>
      <button @click="editor.chain().focus().setParagraph().run()" :class="{ 'is-active': editor.isActive('paragraph') }">
        P
      </button>
      <button @click="editor.chain().focus().toggleHeading({ level: 2 }).run()" :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }">
        H2
      </button>
      
      <div class="divider"></div>

      <button @click="handleAI('polish')" class="ai-tool-btn" title="润色选中的文本">
        ✨ 润色
      </button>
      <button @click="handleAI('rewrite')" class="ai-tool-btn" title="改写选中的文本">
        🔄 改写
      </button>
    </div>

    <!-- 气泡菜单已移除，功能移动到工具栏 -->
    
    <editor-content :editor="editor" class="editor-content" />

    <!-- 底部 AI 栏 -->
    <div class="ai-bar">
      <button @click="handleAI('continue')" :disabled="loading" class="ai-main-btn">
        {{ loading ? "AI 正在思考..." : "🖊️ AI 续写" }}
      </button>
      <div v-if="loading" class="ai-status">正在生成中...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount, watch } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import BubbleMenuExtension from '@tiptap/extension-bubble-menu'
import { aiApi, API_BASE } from '../api'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  novelId: {
    type: [String, Number],
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const loading = ref(false)

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    BubbleMenuExtension.configure({
      pluginKey: 'bubbleMenu',
    }),
    Placeholder.configure({
      placeholder: '开始你的创作...',
    }),
  ],
  editorProps: {
    attributes: {
      class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-2xl mx-auto focus:outline-none',
    },
  },
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  },
})

watch(() => props.modelValue, (newValue) => {
  const isSame = editor.value?.getHTML() === newValue
  if (!isSame && editor.value) {
    editor.value.commands.setContent(newValue, false)
  }
})

async function handleAI(mode) {
  if (!editor.value) return
  
  loading.value = true
  try {
    const selection = editor.value.state.selection
    const selectedText = editor.value.state.doc.textBetween(selection.from, selection.to, ' ')
    
    // 获取前文（简单取最后 1000 字）
    const fullText = editor.value.getText()
    const previousText = fullText.slice(Math.max(0, fullText.length - 1000))

    const provider = localStorage.getItem('novel_ai_provider')
    const model = localStorage.getItem('novel_ai_model')
    const apiKey = localStorage.getItem('novel_ai_api_key')
    const baseUrl = localStorage.getItem('novel_ai_base_url')

    const payload = {
      mode: mode,
      context: {
        previous_text: previousText,
        target_text: selectedText || undefined, // 如果没选中文本，target_text 为空
        style: 'normal'
      },
      stream: true,
      novel_id: props.novelId,
      provider: provider || undefined,
      model: model || undefined,
      api_key: apiKey || undefined,
      base_url: baseUrl || undefined
    }

    // 如果是改写/润色但没选中文本，提示一下
    if ((mode === 'rewrite' || mode === 'polish') && !selectedText) {
      alert("请先选择要处理的文本")
      loading.value = false
      return
    }

    // 使用原生 fetch 实现流式接收
    const response = await fetch(`${API_BASE}/api/ai/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      throw new Error(`请求失败: ${response.statusText}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ""

    // 如果是润色/改写，先删除原文本，准备插入新文本
    // 注意：流式输出时，我们可能希望逐字显示。
    // 简单起见，先在光标处插入（续写），或者替换（改写）。
    if (mode === 'rewrite' || mode === 'polish') {
      editor.value.commands.deleteSelection()
    }

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
            const chunk = data.content || ""
            if (chunk) {
              // 插入内容
              editor.value.commands.insertContent(chunk)
              // 滚动到底部（如果是续写）
              if (mode === 'continue') {
                // editor.value.commands.scrollIntoView() // 有时会跳动，视情况开启
              }
            }
          } catch (e) {
            console.error("解析 SSE 数据失败", e)
          }
        }
      }
    }

  } catch (err) {
    console.error(err)
    alert("AI 请求失败: " + err.message)
  } finally {
    loading.value = false
  }
}

onBeforeUnmount(() => {
  editor.value?.destroy()
})
</script>

<style scoped>
.editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  position: relative;
}

.editor-toolbar {
  padding: 8px;
  border-bottom: 1px solid #eee;
  display: flex;
  gap: 8px;
  background: #f9f9f9;
  border-radius: 8px 8px 0 0;
}

.editor-toolbar button {
  padding: 4px 8px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 4px;
}

.editor-toolbar button.is-active {
  background: #333;
  color: white;
}

.divider {
  width: 1px;
  background: #ddd;
  margin: 0 4px;
}

.ai-tool-btn {
  background: #eef2ff !important;
  border-color: #c7d2fe !important;
  color: #4f46e5 !important;
}

.ai-tool-btn:hover {
  background: #e0e7ff !important;
}

.editor-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  font-size: 16px;
  line-height: 1.6;
}

/* Tiptap 内部样式 */
:deep(.ProseMirror) {
  min-height: 100%;
  outline: none;
}

:deep(.ProseMirror p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  float: left;
  color: #adb5bd;
  pointer-events: none;
  height: 0;
}

/* 气泡菜单 */
.bubble-menu {
  display: flex;
  gap: 8px;
  background: white;
  padding: 6px;
  border-radius: 6px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border: 1px solid #eee;
}

.ai-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: opacity 0.2s;
}

.ai-btn:hover {
  opacity: 0.9;
}

.ai-btn.small {
  padding: 4px 8px;
  font-size: 12px;
}

/* 底部 AI 栏 */
.ai-bar {
  padding: 12px;
  border-top: 1px solid #eee;
  background: #fdfdfd;
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-main-btn {
  background: #333;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.ai-main-btn:disabled {
  background: #999;
  cursor: not-allowed;
}

.ai-status {
  font-size: 12px;
  color: #666;
}
</style>
