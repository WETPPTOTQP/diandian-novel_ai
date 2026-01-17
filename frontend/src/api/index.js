export const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:5000";

async function request(path, options = {}) {
  const url = API_BASE + path;
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const res = await fetch(url, { ...options, headers });
  const contentType = res.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const data = isJson ? await res.json() : await res.text();
  if (!res.ok) {
    const message = typeof data === "string" ? data : data?.message || "请求失败";
    throw new Error(message);
  }
  return data;
}

export const authApi = {
  register: (payload) => request("/api/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  login: (payload) => request("/api/auth/login", { method: "POST", body: JSON.stringify(payload) })
};

export const aiApi = {
  generate: (payload) => request("/api/ai/generate", { method: "POST", body: JSON.stringify(payload) }),
  brainstorm: (payload) => request("/api/ai/brainstorm", { method: "POST", body: JSON.stringify(payload) }),
  listModels: () => request("/api/ai/models")
};

export const novelApi = {
  getStats: () => request("/api/stats"),
  listNovels: () => request("/api/novels"),
  createNovel: (payload) => request("/api/novels", { method: "POST", body: JSON.stringify(payload) }),
  updateNovel: (novelId, payload) => request(`/api/novels/${novelId}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteNovel: (novelId) => request(`/api/novels/${novelId}`, { method: "DELETE" }),
  listChapters: (novelId) => request(`/api/novels/${novelId}/chapters`),
  createChapter: (novelId, payload) =>
    request(`/api/novels/${novelId}/chapters`, { method: "POST", body: JSON.stringify(payload) }),
  getChapter: (chapterId) => request(`/api/chapters/${chapterId}`),
  updateChapter: (chapterId, payload) =>
    request(`/api/chapters/${chapterId}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteChapter: (chapterId) => request(`/api/chapters/${chapterId}`, { method: "DELETE" }),
    
  // Character APIs
  listCharacters: (novelId) => request(`/api/novels/${novelId}/characters`),
  createCharacter: (novelId, payload) =>
    request(`/api/novels/${novelId}/characters`, { method: "POST", body: JSON.stringify(payload) }),
  updateCharacter: (charId, payload) =>
    request(`/api/characters/${charId}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteCharacter: (charId) => request(`/api/characters/${charId}`, { method: "DELETE" }),

  // Idea APIs
  listIdeas: (novelId) => request(`/api/novels/${novelId}/ideas`),
  createIdea: (novelId, payload) =>
    request(`/api/novels/${novelId}/ideas`, { method: "POST", body: JSON.stringify(payload) }),
  deleteIdea: (ideaId) => request(`/api/ideas/${ideaId}`, { method: "DELETE" }),

  // Version Control APIs
  listVersions: (chapterId) => request(`/api/chapters/${chapterId}/versions`),
  createVersion: (chapterId, payload) => 
    request(`/api/chapters/${chapterId}/versions`, { method: "POST", body: JSON.stringify(payload) }),
  restoreVersion: (chapterId, versionId) => 
    request(`/api/chapters/${chapterId}/restore/${versionId}`, { method: "POST" }),
  deleteVersion: (versionId) => request(`/api/versions/${versionId}`, { method: "DELETE" })
};

