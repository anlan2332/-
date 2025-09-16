# 百考通AI写作平台后端

一个功能完整的Flask后端服务，为百考通AI写作平台提供API支持。

## 🚀 功能特性

### 核心功能模块
- **论文生成模块**: 智能标题生成、大纲生成、内容撰写
- **文献检索模块**: 学术文献搜索、论文详情获取、参考文献生成
- **AI聊天模块**: 智能对话、写作指导、实时问答
- **内容优化模块**: 论文润色、AI降重、格式调整

### API接口
- **论文相关API** (`/api/paper/`)
  - `POST /api/paper/generate-title` - 生成论文标题
  - `POST /api/paper/generate-outline` - 生成论文大纲
  - `POST /api/paper/generate-content` - 生成论文内容
  - `POST /api/paper/polish-content` - 润色内容
  - `POST /api/paper/reduce-ai-detection` - AI降重
  - `POST /api/paper/format-paper` - 格式调整

- **文献检索API** (`/api/research/`)
  - `POST /api/research/search-literature` - 搜索文献
  - `POST /api/research/get-paper-details` - 获取论文详情
  - `POST /api/research/generate-references` - 生成参考文献
  - `POST /api/research/analyze-trends` - 分析研究趋势
  - `POST /api/research/recommend-topics` - 推荐研究主题

- **聊天API** (`/api/chat/`)
  - `POST /api/chat/send-message` - 发送消息
  - `GET /api/chat/get-conversation` - 获取对话历史
  - `POST /api/chat/clear-conversation` - 清空对话

## 🛠️ 技术栈

- **后端框架**: Flask 3.0+
- **AI集成**: OpenAI GPT API
- **数据存储**: SQLite (可扩展为PostgreSQL/MySQL)
- **环境管理**: python-dotenv
- **跨域支持**: Flask-CORS
- **API文档**: 内置健康检查和状态监控

## 📦 安装和启动

### 方法一：傻瓜式启动（推荐）
```bash
# 进入后端目录
cd baikaotong-backend

# 运行启动脚本（自动安装依赖并启动）
python start.py
```

### 方法二：手动安装
```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务器
python src/main.py
```

## ⚙️ 配置说明

### 环境变量配置
在 `.env` 文件中配置以下变量：

```env
# OpenAI API配置
OPENAI_API_KEY=039c31ba-ebd5-429b-8e88-593eb0e0dc67
OPENAI_API_BASE=https://api.openai.com/v1

# 联网搜索API配置（用于文献检索）
RESEARCH_API_KEY=039c31ba-ebd5-429b-8e88-593eb0e0dc67
RESEARCH_API_BASE=https://api.openai.com/v1

# 服务器配置
FLASK_ENV=development
FLASK_DEBUG=True
HOST=0.0.0.0
PORT=5000

# 数据库配置
DATABASE_URL=sqlite:///app.db
```

### API密钥说明
- `OPENAI_API_KEY`: 用于一般的AI文本生成功能
- `RESEARCH_API_KEY`: 用于联网文献检索功能

## 🔧 开发指南

### 项目结构
```
baikaotong-backend/
├── src/
│   ├── main.py              # 主应用入口
│   ├── routes/
│   │   ├── paper.py         # 论文相关API
│   │   ├── research.py      # 文献检索API
│   │   └── chat.py          # 聊天API
│   └── utils/
│       └── ai_client.py     # AI客户端工具
├── venv/                    # 虚拟环境
├── .env                     # 环境配置
├── requirements.txt         # 依赖列表
├── start.py                 # 启动脚本
├── install.py               # 安装脚本
└── README.md               # 说明文档
```

### 添加新功能
1. 在 `src/routes/` 目录下创建新的路由文件
2. 在 `src/main.py` 中注册新的蓝图
3. 更新 `requirements.txt` 如果需要新依赖
4. 测试API接口

### 修改AI模型
在 `src/utils/ai_client.py` 中修改AI客户端配置：
```python
# 修改模型参数
MODEL_NAME = "gpt-3.5-turbo"  # 或其他模型
TEMPERATURE = 0.7
MAX_TOKENS = 2000
```

## 🧪 测试

### API健康检查
```bash
curl http://localhost:5000/api/health
```

### 测试论文标题生成
```bash
curl -X POST http://localhost:5000/api/paper/generate-title \
  -H "Content-Type: application/json" \
  -d '{"keywords": "人工智能", "education": "本科", "field": "计算机科学"}'
```

## 🚀 部署

### 开发环境
```bash
python start.py
```
服务器将在 `http://localhost:5000` 启动

### 生产环境
建议使用 Gunicorn 或 uWSGI：
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

## 📝 API文档

### 响应格式
所有API响应都遵循统一格式：
```json
{
  "success": true,
  "message": "操作成功",
  "data": {},
  "timestamp": "2025-09-16T04:21:56"
}
```

### 错误处理
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-09-16T04:21:56"
}
```

## 🔒 安全说明

- API密钥存储在环境变量中，不会暴露在代码中
- 支持CORS跨域请求，可配置允许的域名
- 建议在生产环境中使用HTTPS
- 可以添加API限流和认证机制

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

MIT License

## 🆘 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查找占用端口的进程
   lsof -i :5000
   # 杀死进程
   kill -9 <PID>
   ```

2. **依赖安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   # 清除缓存
   pip cache purge
   ```

3. **API密钥无效**
   - 检查 `.env` 文件中的API密钥是否正确
   - 确认API密钥有足够的权限和余额

4. **虚拟环境问题**
   ```bash
   # 删除虚拟环境
   rm -rf venv
   # 重新创建
   python -m venv venv
   ```

## 📞 支持

如有问题，请：
1. 查看日志文件
2. 检查API文档
3. 提交Issue到项目仓库

---

**版本**: 1.0.0  
**作者**: AI Assistant  
**更新时间**: 2025-09-16

