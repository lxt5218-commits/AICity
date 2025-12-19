# AI 读城 - 城市深度解构平台

> 拨开时代烟尘，触碰城市最深处的灵魂。

一个基于 AI 的城市深度解构平台，通过全网检索和 AI 分析，为你呈现城市的多元视角和文化肌理。

## ✨ 功能特性

- **智能检索**：从 25+ 个维度（知乎、豆瓣、小红书、公众号、微博、B站、音乐、旅行等）随机抽取 6 个不同来源
- **AI 城市侧写**：使用 Groq Llama 3.3 模型生成充满人文温情的城市介绍
- **散文化表达**：拒绝生硬的列表格式，用优美的散文段落娓娓道来
- **动态打捞**：每次搜索随机抽取不同维度，点击"再次打捞"获取全新视角
- **精美 UI**：现代化设计，打字机效果，仪式感的城市解构标题

## 🛠️ 技术栈

### 后端
- **Flask** - Python Web 框架
- **Groq API** - AI 文本生成（Llama 3.3-70b-versatile）
- **Serper API** - 全网搜索服务
- **Flask-CORS** - 跨域支持

### 前端
- **纯 HTML/CSS/JavaScript** - 无框架依赖
- **响应式设计** - 适配各种屏幕尺寸

## 📦 项目结构

```
AICity/
├── app.py              # Flask 后端主文件
├── Index.html          # 前端主页面
├── requirements.txt    # Python 依赖
├── .gitignore         # Git 忽略配置
├── config_local.py    # 本地配置文件（不提交）
└── README.md          # 项目说明文档
```

## 🚀 快速开始

### 本地开发

1. **克隆项目**
   ```bash
   git clone https://github.com/你的用户名/AICity.git
   cd AICity
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置密钥**
   
   创建 `config_local.py` 文件（已在 .gitignore 中）：
   ```python
   SERPER_KEY = "你的_serper_key"
   GROQ_KEY = "你的_groq_key"
   ```

4. **启动后端**
   ```bash
   python app.py
   ```
   
   看到以下输出说明启动成功：
   ```
   ✨ AI 读城后端引擎已就绪 | 端口: 5000
   * Running on http://127.0.0.1:5000
   ```

5. **打开前端**
   
   在浏览器中打开 `Index.html`，或使用 Live Server。

### 环境变量配置

项目支持两种配置方式：

1. **环境变量**（推荐用于生产环境）
   ```bash
   export SERPER_KEY="你的_serper_key"
   export GROQ_KEY="你的_groq_key"
   ```

2. **本地配置文件**（仅用于本地开发）
   - 创建 `config_local.py` 文件
   - 已在 `.gitignore` 中，不会被提交到 Git

## 🌐 部署到 Zeabur

### 1. 准备代码

确保以下文件已准备好：
- ✅ `app.py` - 后端主文件
- ✅ `Index.html` - 前端文件
- ✅ `requirements.txt` - 依赖文件
- ✅ `.gitignore` - Git 配置

### 2. 推送到 GitHub

```bash
git init
git add .
git commit -m "AI City - Ready for deployment"
git remote add origin https://github.com/你的用户名/你的仓库名.git
git branch -M main
git push -u origin main
```

### 3. 在 Zeabur 上部署

1. 访问 [Zeabur](https://zeabur.com)，用 GitHub 登录
2. 创建新项目（Project）
3. 点击 "Add Service" → 选择 "From Git"
4. 选择你的 GitHub 仓库

### 4. 配置服务

- **Language**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
  - 或使用 gunicorn：`gunicorn app:app --bind 0.0.0.0:$PORT`

### 5. 设置环境变量

在 Zeabur 服务的 "Environment Variables" 中添加：

- `SERPER_KEY` = 你的 Serper API Key
- `GROQ_KEY` = 你的 Groq API Key

### 6. 更新前端 API 地址

部署完成后，Zeabur 会给你一个域名（如：`https://ai-city.zeabur.app`）

在 `Index.html` 中找到：
```javascript
fetch('http://127.0.0.1:5000/api/search', {
```

改为：
```javascript
fetch('https://你的域名.zeabur.app/api/search', {
```

## 📡 API 接口

### 健康检查
```
GET /health
```
返回：`{"status": "ok"}`

### 城市搜索
```
POST /api/search
Content-Type: application/json

{
  "city": "北京"
}
```

返回：
```json
{
  "city": "北京",
  "summary": "AI 生成的城市介绍...",
  "results": [
    {
      "title": "结果标题",
      "link": "https://...",
      "snippet": "结果描述",
      "source": "知乎"
    }
  ]
}
```

## 🎨 来源维度（25+ 个）

项目支持从以下维度随机抽取：

- **社交媒体**：知乎、豆瓣、小红书、微博、公众号、贴吧
- **视频/音频**：抖音、快手、B站、音乐、播客
- **生活服务**：点评、美团、旅行
- **权威/学术**：网页、本地、地方志、地图、学术、国家地理、博物馆
- **媒体资讯**：新闻、资讯、澎湃
- **文化艺术**：艺术

每次搜索随机抽取 6 个不同维度，确保内容的多样性和新鲜感。

## 🔧 配置说明

### 后端配置

- **端口**：默认 5000，可通过 `PORT` 环境变量修改
- **CORS**：已开启，允许所有来源访问（生产环境可收紧）

### 前端配置

- **API 地址**：在 `Index.html` 中修改 `fetch` 的 URL
- **样式**：所有样式都在 `<style>` 标签中，可直接修改

## 📝 开发说明

### 添加新的来源维度

1. 在 `app.py` 的 `ALL_SOURCES` 列表中添加新来源
2. 在 `Index.html` 的 `getSourceStyle` 函数中添加对应的颜色配置

### 修改 AI Prompt

编辑 `app.py` 中的 `get_ai_insight` 函数，修改 prompt 内容。

## 🐛 常见问题

### 后端启动失败

- 检查是否安装了所有依赖：`pip install -r requirements.txt`
- 检查密钥是否正确配置
- 检查端口是否被占用

### 前端无法连接后端

- 检查后端是否正在运行
- 检查 API 地址是否正确
- 检查浏览器控制台是否有 CORS 错误

### Groq API 调用失败

- 检查 `GROQ_KEY` 是否正确
- 检查网络连接
- 查看后端日志中的错误信息

## 📄 许可证

本项目仅供学习和研究使用。

## 🙏 致谢

- [Groq](https://groq.com) - AI 文本生成服务
- [Serper](https://serper.dev) - 搜索 API 服务
- [Zeabur](https://zeabur.com) - 部署平台

---

**拨开时代烟尘，触碰城市最深处的灵魂。**

