<template>
  <div class="write-layout">
    <!-- 左侧章节列表 -->
    <aside class="sidebar">
      <div class="sidebar-header">
      <router-link to="/" class="back-home">← 首页</router-link>
    </div>
    <div class="sidebar-header">
      <h3>目录</h3>
      <span v-if="saving" class="save-status">保存中...</span>
      <span v-else-if="lastSaved" class="save-status">已保存</span>
    </div>
      <ul>
        <li 
          v-for="chapter in chapters" 
          :key="chapter.id" 
          :class="{ active: currentChapterId === chapter.id }"
          @click="selectChapter(chapter)"
          class="chapter-item"
        >
          <span class="chapter-title">{{ chapter.title }}</span>
          <button @click.stop="confirmDeleteChapter(chapter)" class="delete-chapter-btn">×</button>
        </li>
      </ul>
      <button class="add-chapter" @click="createNewChapter" :disabled="loading">+ 新建章节</button>
    </aside>

    <!-- 中间编辑区 -->
    <main class="main-content">
      <template v-if="currentChapterId">
        <header class="chapter-header">
          <input 
            v-model="chapterTitle" 
            @change="saveCurrentChapter"
            placeholder="章节标题" 
            class="title-input" 
          />
        </header>
        <div class="editor-wrapper">
          <Editor 
            :model-value="chapterContent" 
            :novel-id="novelId"
            @update:modelValue="val => { chapterContent = val; handleContentChange(val); }"
          />
        </div>
      </template>
      <div v-else class="empty-state">
        <p>请选择或新建一个章节开始写作</p>
      </div>
    </main>

    <!-- 右侧辅助栏 -->
    <aside class="aux-sidebar">
      <div class="aux-tabs">
        <button 
          :class="{ active: activeTab === 'settings' }" 
          @click="activeTab = 'settings'"
        >设定</button>
        <button 
          :class="{ active: activeTab === 'history' }" 
          @click="activeTab = 'history'"
        >历史版本</button>
      </div>

      <div v-show="activeTab === 'settings'" class="aux-content">
        <h3>AI 助手 & 设定</h3>
        <div v-if="currentNovel" class="aux-card">
          <h4>当前设定</h4>
          <div class="setting-item">
            <label>简介 / 故事背景</label>
            <textarea 
              v-model="currentNovel.summary" 
              @change="saveNovelSettings"
              placeholder="输入故事背景、世界观..."
              rows="5"
            ></textarea>
          </div>
          <div class="setting-item">
            <label>标签 / 风格</label>
            <input 
              v-model="currentNovel.tags" 
              @change="saveNovelSettings"
              placeholder="例如：赛博朋克, 悬疑"
            />
          </div>
          <div class="status-hint">
            {{ settingsSaving ? "保存中..." : "修改自动保存" }}
          </div>
        </div>
      </div>

      <div v-show="activeTab === 'history'" class="aux-content">
        <div class="history-header">
          <h3>版本控制</h3>
          <button @click="createVersion" class="create-version-btn" :disabled="!currentChapterId">
            + 保存快照
          </button>
        </div>
        
        <div v-if="!currentChapterId" class="empty-hint">请先选择章节</div>
        <div v-else-if="versions.length === 0" class="empty-hint">暂无历史版本</div>
        
        <ul v-else class="version-list">
          <li v-for="v in versions" :key="v.id" class="version-item">
            <div class="version-info">
              <span class="version-time">{{ formatDate(v.created_at) }}</span>
              <span class="version-note" v-if="v.note">{{ v.note }}</span>
            </div>
            <div class="version-actions">
              <button @click="restoreVersion(v)" class="restore-btn" title="回滚到此版本">回滚</button>
              <button @click="deleteVersion(v.id)" class="delete-ver-btn" title="删除">×</button>
            </div>
          </li>
        </ul>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import Editor from "../components/Editor.vue";
import { novelApi } from "../api";

const route = useRoute();
const novelId = ref(route.params.id); // 从路由获取 ID
const currentNovel = ref(null);
const chapters = ref([]);
const currentChapterId = ref(null);
const chapterTitle = ref("");
const chapterContent = ref("");

const activeTab = ref('settings');
const versions = ref([]);

const loading = ref(false);
const saving = ref(false);
const lastSaved = ref(false);
const settingsSaving = ref(false);
let saveTimer = null;

// 初始化：获取指定小说信息
onMounted(async () => {
  if (!novelId.value) {
    alert("未指定小说 ID");
    return;
  }

  try {
    // 这里需要一个获取单个小说详情的接口，目前只能先从列表中筛选（或者后端补充 getNovel 接口）
    // 为了稳健，先用 listNovels 筛选，后续优化后端
    const res = await novelApi.listNovels();
    const novels = res.data || [];
    const target = novels.find(n => n.id == novelId.value);
    
    if (target) {
      currentNovel.value = target;
    } else {
      alert("小说不存在");
      return;
    }
    
    await loadChapters();
    
  } catch (err) {
    console.error("初始化失败", err);
    alert("加载失败: " + err.message);
  }
});

async function saveNovelSettings() {
  if (!currentNovel.value) return;
  settingsSaving.value = true;
  try {
    await novelApi.updateNovel(currentNovel.value.id, {
      summary: currentNovel.value.summary,
      tags: currentNovel.value.tags
    });
  } catch (err) {
    console.error("保存设定失败", err);
  } finally {
    settingsSaving.value = false;
  }
}

async function loadChapters() {
  if (!novelId.value) return;
  try {
    const res = await novelApi.listChapters(novelId.value);
    chapters.value = res.data || [];
    
    // 如果有章节且当前未选中，默认选中第一章
    if (chapters.value.length > 0 && !currentChapterId.value) {
      selectChapter(chapters.value[0]);
    }
  } catch (err) {
    console.error("加载章节失败", err);
  }
}

async function selectChapter(chapter) {
  // 切换前先保存当前章节（如果需要）
  if (currentChapterId.value) {
    await saveCurrentChapter();
  }

  currentChapterId.value = chapter.id;
  chapterTitle.value = chapter.title;
  // 加载章节详细内容
  try {
    const res = await novelApi.getChapter(chapter.id);
    chapterContent.value = res.data.content || "";
    lastSaved.value = false;
    
    // 加载该章节的历史版本
    loadVersions(chapter.id);
  } catch (err) {
    console.error("加载章节内容失败", err);
    chapterContent.value = "";
  }
}

async function loadVersions(chapterId) {
  try {
    const res = await novelApi.listVersions(chapterId);
    versions.value = res.data || [];
  } catch (err) {
    console.error("加载版本历史失败", err);
  }
}

async function createVersion() {
  if (!currentChapterId.value) return;
  const note = prompt("请输入版本备注（可选）：");
  if (note === null) return; // Cancelled
  
  try {
    await novelApi.createVersion(currentChapterId.value, { note });
    await loadVersions(currentChapterId.value);
    alert("快照保存成功");
  } catch (err) {
    alert("保存快照失败: " + err.message);
  }
}

async function restoreVersion(version) {
  if (!confirm(`确定要回滚到 ${formatDate(version.created_at)} 的版本吗？当前未保存的内容将丢失。`)) return;
  
  // 清除待保存的定时器，防止回滚后被旧内容的自动保存覆盖
  if (saveTimer) {
    clearTimeout(saveTimer);
    saveTimer = null;
  }
  saving.value = false;
  
  try {
    await novelApi.restoreVersion(currentChapterId.value, version.id);
    // 重新加载章节内容
    const res = await novelApi.getChapter(currentChapterId.value);
    chapterContent.value = res.data.content || "";
    // 强制刷新编辑器组件，确保内容更新
    editorKey.value++;
    lastSaved.value = true; // 标记为已保存
    alert("回滚成功");
  } catch (err) {
    alert("回滚失败: " + err.message);
  }
}

async function deleteVersion(versionId) {
  if (!confirm("确定删除此历史版本吗？")) return;
  try {
    await novelApi.deleteVersion(versionId);
    await loadVersions(currentChapterId.value);
  } catch (err) {
    alert("删除失败: " + err.message);
  }
}

function formatDate(isoStr) {
  if (!isoStr) return "";
  const date = new Date(isoStr);
  return date.toLocaleString();
}

async function createNewChapter() {
  if (!novelId.value) return;
  loading.value = true;
  try {
    const count = chapters.value.length + 1;
    const res = await novelApi.createChapter(novelId.value, {
      title: `第${count}章`
    });
    await loadChapters();
    
    // 选中新创建的章节
    const newChapterId = res.data.id;
    const newChapter = chapters.value.find(c => c.id === newChapterId);
    if (newChapter) {
      selectChapter(newChapter);
    }
  } catch (err) {
    alert("创建章节失败: " + err.message);
  } finally {
    loading.value = false;
  }
}

async function confirmDeleteChapter(chapter) {
  if (confirm(`确定要删除章节《${chapter.title}》吗？`)) {
    try {
      await novelApi.deleteChapter(chapter.id);
      
      // 如果删除的是当前选中章节，清空选中状态
      if (currentChapterId.value === chapter.id) {
        currentChapterId.value = null;
        chapterTitle.value = "";
        chapterContent.value = "";
      }
      
      await loadChapters();
    } catch (err) {
      alert("删除失败: " + err.message);
    }
  }
}

// 防抖自动保存
function handleContentChange(newContent) {
  if (saveTimer) clearTimeout(saveTimer);
  lastSaved.value = false;
  saving.value = true;
  
  saveTimer = setTimeout(() => {
    saveCurrentChapter();
  }, 2000); // 2秒后自动保存
}

async function saveCurrentChapter() {
  if (!currentChapterId.value) return;
  
  try {
    await novelApi.updateChapter(currentChapterId.value, {
      title: chapterTitle.value,
      content: chapterContent.value
    });
    saving.value = false;
    lastSaved.value = true;
    
    // 更新左侧列表中的标题
    const chapter = chapters.value.find(c => c.id === currentChapterId.value);
    if (chapter) {
      chapter.title = chapterTitle.value;
    }
  } catch (err) {
    console.error("保存失败", err);
    saving.value = false;
  }
}
</script>

<style scoped>
.write-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  background: #f8f9fa;
  border-right: 1px solid #ddd;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
}

.back-home {
  text-decoration: none;
  color: #666;
  font-size: 14px;
}

.save-status {
  font-size: 12px;
  color: #28a745;
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
  overflow-y: auto;
}

.chapter-item {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chapter-item:hover {
  background: #f0f0f0;
}

.chapter-item.active {
  background: #e3f2fd;
  color: #007bff;
}

.chapter-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.delete-chapter-btn {
  background: transparent;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0 4px;
  font-size: 18px;
  line-height: 1;
  opacity: 0;
  transition: opacity 0.2s;
}

.chapter-item:hover .delete-chapter-btn {
  opacity: 1;
}

.delete-chapter-btn:hover {
  color: #dc3545;
}

.add-chapter {
  padding: 12px;
  background: #fff;
  border: none;
  border-top: 1px solid #ddd;
  cursor: pointer;
  color: #007bff;
  font-weight: 500;
}

.add-chapter:hover {
  background: #f0f7ff;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px 24px;
  max-width: 900px;
  margin: 0 auto;
}

.chapter-header {
  margin-bottom: 16px;
}

.title-input {
  width: 100%;
  font-size: 24px;
  font-weight: bold;
  border: none;
  background: transparent;
  outline: none;
  color: #333;
}

.editor-wrapper {
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  overflow: hidden; /* 让 Editor 组件处理滚动 */
}

.aux-sidebar {
  width: 280px;
  background: white;
  border-left: 1px solid #ddd;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.aux-tabs {
  display: flex;
  margin-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.aux-tabs button {
  flex: 1;
  padding: 8px;
  border: none;
  background: none;
  cursor: pointer;
  font-weight: 500;
  color: #666;
  border-bottom: 2px solid transparent;
}

.aux-tabs button.active {
  color: #007bff;
  border-bottom-color: #007bff;
}

.aux-content {
  flex: 1;
  overflow-y: auto;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-header h3 {
  margin: 0;
  font-size: 16px;
}

.create-version-btn {
  font-size: 12px;
  padding: 4px 8px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.create-version-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.version-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.version-item {
  background: #f8f9fa;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 8px;
}

.version-info {
  margin-bottom: 8px;
}

.version-time {
  font-size: 12px;
  color: #333;
  font-weight: bold;
  display: block;
}

.version-note {
  font-size: 12px;
  color: #666;
  display: block;
  margin-top: 4px;
}

.version-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.restore-btn {
  font-size: 12px;
  padding: 2px 8px;
  border: 1px solid #007bff;
  color: #007bff;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.restore-btn:hover {
  background: #f0f7ff;
}

.delete-ver-btn {
  font-size: 12px;
  padding: 2px 8px;
  border: 1px solid #dc3545;
  color: #dc3545;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.delete-ver-btn:hover {
  background: #fff0f0;
}

.empty-hint {
  text-align: center;
  color: #999;
  font-size: 12px;
  margin-top: 20px;
}

.aux-card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #eee;
}

.setting-item {
  margin-bottom: 12px;
}

.setting-item label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.setting-item textarea,
.setting-item input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  font-family: inherit;
  resize: vertical;
}

.status-hint {
  font-size: 12px;
  color: #999;
  text-align: right;
  margin-top: 4px;
}
</style>
