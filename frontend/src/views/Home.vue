<template>
  <div class="home-container">
    <header class="home-header">
      <h1>Novel AI 创作平台</h1>
      <nav class="main-nav">
        <router-link to="/character" class="nav-btn">人物生成</router-link>
        <router-link to="/ideas" class="nav-btn">灵感构思</router-link>
        <router-link to="/style" class="nav-btn">风格模仿</router-link>
        <router-link to="/profile" class="nav-btn">个人中心</router-link>
      </nav>
    </header>

    <main class="novels-section">
      <div class="section-header">
        <h2>我的作品</h2>
        <button @click="showCreateModal = true" class="create-btn">+ 新建作品</button>
      </div>

      <div class="novels-grid">
        <div 
          v-for="novel in novels" 
          :key="novel.id" 
          class="novel-card"
          @click="openNovel(novel.id)"
        >
          <div class="novel-info">
            <h3>{{ novel.title }}</h3>
            <p class="novel-summary">{{ novel.summary || '暂无简介' }}</p>
            <div class="novel-tags">
              <span v-if="novel.tags" class="tag">{{ novel.tags }}</span>
            </div>
            <div class="novel-meta">
              <span>更新于 {{ formatDate(novel.updated_at) }}</span>
            </div>
            <div class="novel-actions">
              <button @click.stop="exportNovel(novel.id, 'txt')" class="action-btn">TXT</button>
              <button @click.stop="exportNovel(novel.id, 'docx')" class="action-btn">Word</button>
              <button @click.stop="confirmDeleteNovel(novel)" class="action-btn delete-btn">删除</button>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="loading" class="loading">加载中...</div>
      <div v-if="!loading && novels.length === 0" class="empty-state">
        <p>还没有作品，快去创建一个吧！</p>
      </div>
    </main>

    <!-- 新建作品弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal-content">
        <h3>新建作品</h3>
        <input v-model="newNovel.title" placeholder="作品名称" class="modal-input" />
        <textarea v-model="newNovel.summary" placeholder="作品简介（选填）" class="modal-input" rows="3"></textarea>
        <input v-model="newNovel.tags" placeholder="标签（例如：玄幻, 穿越）" class="modal-input" />
        <div class="modal-actions">
          <button @click="showCreateModal = false" class="cancel-btn">取消</button>
          <button @click="createNovel" class="confirm-btn" :disabled="creating">
            {{ creating ? "创建中..." : "创建" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { novelApi, API_BASE } from "../api";

const router = useRouter();
const novels = ref([]);
const loading = ref(false);
const showCreateModal = ref(false);
const creating = ref(false);

const newNovel = ref({
  title: "",
  summary: "",
  tags: ""
});

onMounted(async () => {
  await fetchNovels();
});

async function fetchNovels() {
  loading.value = true;
  try {
    const res = await novelApi.listNovels();
    novels.value = res.data || [];
  } catch (err) {
    console.error("加载作品失败", err);
  } finally {
    loading.value = false;
  }
}

function openNovel(id) {
  router.push(`/write/${id}`);
}

function exportNovel(id, format) {
  window.open(`${API_BASE}/api/novels/${id}/export?format=${format}`, '_blank');
}

async function confirmDeleteNovel(novel) {
  if (confirm(`确定要删除作品《${novel.title}》吗？此操作无法撤销。`)) {
    try {
      await novelApi.deleteNovel(novel.id);
      await fetchNovels(); // 刷新列表
    } catch (err) {
      alert("删除失败: " + err.message);
    }
  }
}

async function createNovel() {
  if (!newNovel.value.title.trim()) {
    alert("请输入作品名称");
    return;
  }
  
  creating.value = true;
  try {
    const res = await novelApi.createNovel({
      title: newNovel.value.title,
      summary: newNovel.value.summary,
      tags: newNovel.value.tags
    });
    
    showCreateModal.value = false;
    newNovel.value = { title: "", summary: "", tags: "" };
    
    // 直接跳转到新作品
    router.push(`/write/${res.data.id}`);
  } catch (err) {
    alert("创建失败: " + err.message);
  } finally {
    creating.value = false;
  }
}

function formatDate(isoStr) {
  if (!isoStr) return "";
  const date = new Date(isoStr);
  return date.toLocaleDateString() + " " + date.toLocaleTimeString().slice(0, 5);
}
</script>

<style scoped>
.home-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.home-header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.nav-btn {
  margin-left: 20px;
  text-decoration: none;
  color: #666;
  font-weight: 500;
}

.nav-btn:hover {
  color: #007bff;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.create-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.create-btn:hover {
  background: #0056b3;
}

.novels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.novel-card {
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.novel-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  border-color: #007bff;
}

.novel-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #333;
}

.novel-summary {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px 0;
  height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.novel-meta {
  font-size: 12px;
  color: #999;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f5f5f5;
}

.novel-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 4px 8px;
  border: 1px solid #ddd;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  color: #666;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #e9ecef;
  border-color: #adb5bd;
  color: #333;
}

.action-btn.delete-btn {
  background: #dc3545;
  color: white;
}

.action-btn.delete-btn:hover {
  background: #c82333;
}

.tag {
  background: #f0f7ff;
  color: #007bff;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  width: 400px;
  max-width: 90%;
}

.modal-content h3 {
  margin-top: 0;
  margin-bottom: 20px;
}

.modal-input {
  display: block;
  width: 100%;
  margin-bottom: 16px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  font-family: inherit;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn {
  background: none;
  border: 1px solid #ddd;
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.confirm-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.confirm-btn:disabled {
  background: #ccc;
}
</style>

