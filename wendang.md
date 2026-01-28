# Novel AI 项目结构

## 后端 (backend/)

### 核心文件
| 文件 | 说明 |
|------|------|
| `app.py` | 应用入口（创建 app、挂载蓝图） |
| `config.py` | 配置加载（环境变量、本地配置） |
| `database.py` | 数据库连接、初始化、Session 管理 |
| `models.py` | ORM 模型定义（User, Novel, Chapter, Character, Idea 等） |
| `novel_ai.py` | AI 核心逻辑封装（调用 Provider 生成内容） |
| `ai_providers.py` | AI 模型提供方适配（Ollama, OpenAI Compat） |
| `context_builder.py` | 构建 AI 上下文（拼接前文、大纲、设定等） |
| `prompts.py` | AI 提示词模板管理 |
| `__main__.py` | 模块入口支持 |
| `requirements.txt` | 后端依赖列表 |

### 路由 (backend/routes/)
| 文件 | 说明 |
|------|------|
| `__init__.py` | 蓝图导出 |
| `ai_routes.py` | AI 生成接口（续写、润色、灵感等） |
| `auth_routes.py` | 用户认证接口（登录、注册） |
| `novel_routes.py` | 小说管理接口（增删改查作品、章节、角色、灵感） |

### 工具 (backend/utils/)
| 文件 | 说明 |
|------|------|
| `security.py` | 密码哈希、Token 生成与验证 |
| `rate_limiter.py` | 简单的请求限流工具 |

---

## 前端 (frontend/)

### 根目录配置
| 文件 | 说明 |
|------|------|
| `index.html` | 入口 HTML 文件 |
| `package.json` | 项目依赖与脚本配置 |
| `vite.config.js` | Vite 构建配置 |

### 源码 (frontend/src/)

#### 入口与路由
| 文件 | 说明 |
|------|------|
| `main.js` | Vue 应用入口，挂载插件 |
| `App.vue` | 根组件 |
| `router.js` | 路由定义与导航守卫 |

#### API (frontend/src/api/)
| 文件 | 说明 |
|------|------|
| `index.js` | 统一 API 封装（Axios 实例及所有请求方法） |

#### 页面 (frontend/src/views/)
| 文件 | 说明 |
|------|------|
| `Home.vue` | 首页：展示作品列表、新建作品 |
| `Write.vue` | 写作页：核心编辑器、章节管理、AI 助手 |
| `Character.vue` | 角色管理页：设定人物卡 |
| `Ideas.vue` | 灵感构思页：管理灵感碎片 |
| `Style.vue` | 风格模仿页（功能开发中） |
| `Profile.vue` | 个人中心：设置与模型配置 |

#### 组件 (frontend/src/components/)
| 文件 | 说明 |
|------|------|
| `Editor.vue` | 封装的文本编辑器组件 |
| `AIButton.vue` | AI 功能触发按钮组件 |

---

## API 接口概览 (参考)

### POST /api/ai/generate
AI 生成接口（续写/改写/润色/扩写）

**请求体 JSON：**
```json
{
  "mode": "continue",           // 模式：continue(续写), rewrite(改写), polish(润色), expand(扩写)
  "model": "ollama/qwen2.5",    // 指定模型（可选）
  "context": {
    "previous_text": "...",      // 前文（续写用）
    "target_text": "...",        // 选中的文本（改写/润色用）
    "character_summary": "...",  // 角色简述（可选，用于增强一致性）
    "style": "dark_fantasy"      // 风格标签
  },
  "stream": true                 // 是否流式返回
}
```

### POST /api/ai/brainstorm
AI 灵感碰撞接口（大纲/人设/世界观）

**请求体 JSON：**
```json
{
  "type": "outline",                                    // outline(大纲), character(人设), world(世界观)
  "keywords": ["赛博朋克", "侦探", "下雨"],
  "instruction": "生成一个三幕式大纲"
}
```

### 根目录其他文件
| 文件 | 说明 |
|------|------|
| `.env` | **核心配置**（API Key、数据库路径等） |
| `start.bat` | Windows 一键启动脚本 |
| `novels.db` | SQLite 数据库文件 |
| `README.md` | 项目说明文档 |
