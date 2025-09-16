# 百考通AI写作平台前端

一个现代化的React前端应用，为百考通AI写作平台提供用户界面。

## 🚀 功能特性

### 核心功能
- **智能论文生成**: 标题生成、大纲创建、内容撰写
- **AI聊天助手**: 实时对话、写作指导、问题解答
- **文献检索**: 学术资源搜索、参考文献管理
- **内容优化**: 论文润色、AI降重、格式调整
- **响应式设计**: 完美适配桌面和移动设备

### 用户界面
- **现代化设计**: 基于Tailwind CSS和shadcn/ui组件库
- **直观操作**: 简洁的表单设计和交互流程
- **实时反馈**: 加载状态、错误提示、成功通知
- **可访问性**: 符合Web可访问性标准

## 🛠️ 技术栈

- **前端框架**: React 18
- **构建工具**: Vite
- **样式框架**: Tailwind CSS
- **组件库**: shadcn/ui
- **图标库**: Lucide React
- **状态管理**: React Hooks
- **HTTP客户端**: Fetch API
- **开发语言**: JavaScript/JSX

## 📦 安装和启动

### 快速开始
```bash
# 进入前端目录
cd baikaotong-ai

# 安装依赖
pnpm install

# 启动开发服务器
pnpm run dev
```

### 其他包管理器
```bash
# 使用npm
npm install
npm run dev

# 使用yarn
yarn install
yarn dev
```

## 🔧 开发指南

### 项目结构
```
baikaotong-ai/
├── src/
│   ├── components/
│   │   ├── ui/                 # 基础UI组件
│   │   ├── PaperForm.jsx       # 论文表单组件
│   │   └── ChatWindow.jsx      # 聊天窗口组件
│   ├── services/
│   │   └── api.js              # API服务
│   ├── assets/
│   │   └── logo.jpg            # 静态资源
│   ├── App.jsx                 # 主应用组件
│   ├── App.css                 # 全局样式
│   └── main.jsx                # 应用入口
├── public/                     # 公共资源
├── index.html                  # HTML模板
├── package.json                # 项目配置
├── tailwind.config.js          # Tailwind配置
├── vite.config.js              # Vite配置
└── README.md                   # 说明文档
```

### 组件说明

#### PaperForm.jsx
论文生成表单组件，包含：
- 标题输入和智能选题
- 学历和字数选择
- 语言和图表选项
- 文件上传功能
- 补充说明输入
- 快捷操作按钮
- 大纲生成和显示

#### ChatWindow.jsx
AI聊天窗口组件，包含：
- 消息列表显示
- 实时消息发送
- 对话历史管理
- 窗口最小化/展开
- 加载状态显示

#### API服务 (api.js)
统一的API调用服务，包含：
- 请求封装和错误处理
- 论文相关API调用
- 文献检索API调用
- 聊天API调用
- 环境配置管理

### 自定义配置

#### API基础URL配置
在 `src/services/api.js` 中修改：
```javascript
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '' // 生产环境使用相对路径
  : 'http://localhost:5000'; // 开发环境使用本地后端
```

#### 样式主题配置
在 `tailwind.config.js` 中修改：
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        // 自定义颜色
        primary: '#3b82f6',
        secondary: '#64748b',
      }
    }
  }
}
```

## 🧪 测试

### 开发环境测试
```bash
# 启动开发服务器
pnpm run dev

# 在浏览器中访问
http://localhost:5173
```

### 功能测试清单
- [x] 智能选题功能
- [x] 大纲生成功能
- [x] 聊天对话功能
- [x] 表单验证
- [x] 响应式布局
- [x] 错误处理

## 🚀 构建和部署

### 构建生产版本
```bash
# 构建项目
pnpm run build

# 预览构建结果
pnpm run preview
```

### 部署选项

#### 静态部署
构建后的 `dist` 目录可以部署到任何静态文件服务器：
- Netlify
- Vercel
- GitHub Pages
- 阿里云OSS
- 腾讯云COS

#### 服务器部署
```bash
# 使用nginx部署
sudo cp -r dist/* /var/www/html/

# 配置nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 🔧 开发工具

### 推荐的VS Code扩展
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Auto Rename Tag
- Bracket Pair Colorizer
- GitLens

### 代码格式化
```bash
# 安装Prettier
npm install --save-dev prettier

# 格式化代码
npx prettier --write src/
```

## 📱 响应式设计

### 断点配置
```javascript
// Tailwind CSS断点
sm: '640px',   // 小屏幕
md: '768px',   // 中等屏幕
lg: '1024px',  // 大屏幕
xl: '1280px',  // 超大屏幕
```

### 移动端优化
- 触摸友好的按钮大小
- 适配移动端的表单输入
- 优化的聊天界面
- 响应式导航菜单

## 🔒 安全考虑

- 输入验证和清理
- XSS防护
- CSRF保护
- 安全的API调用
- 敏感信息保护

## 🎨 UI/UX设计

### 设计原则
- 简洁明了的界面
- 一致的视觉风格
- 直观的用户流程
- 快速的响应反馈

### 颜色方案
- 主色调: 蓝色系 (#3b82f6)
- 辅助色: 灰色系 (#64748b)
- 成功色: 绿色系 (#10b981)
- 警告色: 黄色系 (#f59e0b)
- 错误色: 红色系 (#ef4444)

## 🔄 状态管理

### React Hooks使用
```javascript
// 状态管理示例
const [formData, setFormData] = useState({
  title: '',
  education: '本科',
  wordCount: '8000'
});

// 副作用处理
useEffect(() => {
  loadConversation();
}, []);
```

## 📊 性能优化

### 优化策略
- 组件懒加载
- 图片优化
- 代码分割
- 缓存策略
- 减少重渲染

### 构建优化
```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-select']
        }
      }
    }
  }
}
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

MIT License

## 🆘 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   # 清除缓存
   pnpm store prune
   # 重新安装
   rm -rf node_modules pnpm-lock.yaml
   pnpm install
   ```

2. **开发服务器启动失败**
   ```bash
   # 检查端口占用
   lsof -i :5173
   # 使用其他端口
   pnpm run dev --port 3000
   ```

3. **API调用失败**
   - 检查后端服务是否启动
   - 确认API基础URL配置
   - 查看浏览器控制台错误

4. **样式不生效**
   ```bash
   # 重新构建Tailwind
   npx tailwindcss -i ./src/index.css -o ./dist/output.css --watch
   ```

## 📞 支持

如有问题，请：
1. 查看浏览器控制台
2. 检查网络请求
3. 提交Issue到项目仓库

---

**版本**: 1.0.0  
**作者**: AI Assistant  
**更新时间**: 2025-09-16

