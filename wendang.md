# Novel AI 项目结构

## 后端 (backend/)

### 核心文件
| 文件 | 说明 |
|------|------|
| `app.py` | 应用入口（创建 app、挂载蓝图） |
| `config.py` | 配置加载（环境变量、本地配置） |
| `auth.py` | 登录注册、鉴权中间件 |
| `novel_ai.py` | 写作业务编排（续写/改写/润色/大纲/风格等） |
| `ai_providers.py` | 各种模型提供方封装（Ollama、本家 API 等） |
| `prompts.py` | 所有 AI 模式的 prompt 模板集中管理 |
| `context_builder.py` | 根据作品/章节/人物组合上下文给 AI |

### 路由 (routes/)
| 文件 | 说明 |
|------|------|
| `__init__.py` | 模块初始化 |
| `auth_routes.py` | 登录注册、刷新 token |
| `novel_routes.py` | 作品 CRUD、章节管理 |
| `ai_routes.py` | AI 相关接口（续写、润色、风格模仿等） |
| `idea_routes.py` | 灵感碰撞、情节构思 |
| `profile_routes.py` | 用户配置、用量信息 |

### 数据层
| 文件 | 说明 |
|------|------|
| `models.py` | ORM 模型定义（User、Novel、Chapter 等） |
| `schemas.py` | 接口请求/响应的数据结构（Pydantic 等） |
| `database.py` | 数据库连接、Session 管理 |
| `novels.db` | SQLite 数据库（开发环境） |

### 业务服务 (services/)
| 文件 | 说明 |
|------|------|
| `__init__.py` | 模块初始化 |
| `novel_service.py` | 作品、章节相关业务逻辑 |
| `character_service.py` | 人物卡生成与管理 |
| `idea_service.py` | 情节构思、灵感相关逻辑 |

### 工具 (utils/)
| 文件 | 说明 |
|------|------|
| `__init__.py` | 模块初始化 |
| `logging_utils.py` | 日志封装 |
| `security.py` | 密码散列、token 生成与验证 |
| `rate_limiter.py` | 简单限流/配额（按用户） |

### 测试 (tests/)
| 文件 | 说明 |
|------|------|
| `__init__.py` | 模块初始化 |
| `test_ai_routes.py` | AI 路由测试 |
| `test_auth.py` | 认证测试 |
| `test_novel_routes.py` | 作品路由测试 |

### 其他
| 文件 | 说明 |
|------|------|
| `requirements.txt` | 依赖 |

---

## 前端 (frontend/)

### 配置文件
| 文件 | 说明 |
|------|------|
| `index.html` | 入口 HTML |
| `package.json` | 项目依赖配置 |
| `vite.config.js` | 构建工具配置 |

### 源码 (src/)

#### 入口与路由
| 文件 | 说明 |
|------|------|
| `main.js` | 入口文件 |
| `router.js` | 路由配置 |

#### API 封装 (api/)
| 文件 | 说明 |
|------|------|
| `index.js` | axios 实例、拦截器 |
| `authApi.js` | 登录、注册、用户信息 |
| `novelApi.js` | 作品、章节接口 |
| `aiApi.js` | AI 调用接口（续写、润色、灵感） |
| `profileApi.js` | 用户配置、配额 |

#### 状态管理 (store/)
| 文件 | 说明 |
|------|------|
| `index.js` | 创建 store |
| `userStore.js` | 用户信息、token、角色 |
| `novelStore.js` | 当前作品、章节列表、选中章节 |
| `uiStore.js` | 全局 UI 状态（loading、主题等） |

#### 页面 (views/)
| 文件 | 说明 |
|------|------|
| `Home.vue` | 主页：功能入口、最近作品 |
| `Write.vue` | 写作页：章节列表 + 编辑器 + AI 区域 |
| `Ideas.vue` | 灵感页：关键词→灵感卡片、大纲视图 |
| `Profile.vue` | 个人中心：账号、配额、偏好设置 |
| `Auth.vue` | 登录/注册页（如果需要单独页面） |

#### 组件 (components/)
| 文件 | 说明 |
|------|------|
| `Editor.vue` | 富文本/Markdown 编辑器 |
| `AIButton.vue` | AI 菜单按钮（续写/改写/润色等） |
| `AIPanel.vue` | 展示 AI 结果的侧边/底部面板 |
| `Card.vue` | 通用卡片 |
| `NovelList.vue` | 作品列表 |
| `ChapterList.vue` | 章节列表 |
| `CharacterCard.vue` | 人物卡展示 |

#### 布局组件 (components/Layout/)
| 文件 | 说明 |
|------|------|
| `AppLayout.vue` | 应用布局 |
| `Sidebar.vue` | 侧边栏 |

#### 其他
| 目录/文件 | 说明 |
|-----------|------|
| `assets/` | 静态资源（图标、logo 等） |
| `styles/` | 全局样式 |
| └── `index.css` | 主样式文件 |
| └── `variables.css` | 主题色、字体等 |
| `utils/` | 前端工具函数 |
| └── `storage.js` | 本地存储封装（草稿、token） |
| └── `helpers.js` | 通用小工具（防抖、节流等） |

---

## API 接口

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
