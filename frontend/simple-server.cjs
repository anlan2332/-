const express = require('express');
const multer = require('multer');
const path = require('path');

const app = express();
const PORT = 3000;

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/');
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + '-' + file.originalname);
  }
});
const upload = multer({ storage: storage });

// Create uploads directory if it doesn't exist
const fs = require('fs');
if (!fs.existsSync('uploads')) {
  fs.mkdirSync('uploads');
}

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use('/uploads', express.static('uploads'));

// Main route
app.get('/', (req, res) => {
  res.send(`<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>百考通AI写作平台</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #e8f4fd 0%, #dae8fc 100%);
            min-height: 100vh;
        }
        
        .main-container {
            display: flex;
            height: 100vh;
        }
        
        /* 左侧功能菜单 */
        .sidebar {
            width: 280px;
            background: #fff;
            border-right: 1px solid #e5e7eb;
            box-shadow: 2px 0 10px rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
        }
        
        .sidebar-header {
            padding: 20px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        
        .logo-text {
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
        }
        
        .search-box {
            padding: 15px;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .search-input {
            width: 100%;
            padding: 10px 15px 10px 40px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 14px;
            background: #f9fafb;
            position: relative;
        }
        
        .search-wrapper {
            position: relative;
        }
        
        .search-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: #9ca3af;
            font-size: 14px;
        }
        
        .menu-list {
            flex: 1;
            padding: 10px 0;
            overflow-y: auto;
        }
        
        .menu-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 20px;
            color: #374151;
            text-decoration: none;
            transition: all 0.2s;
            cursor: pointer;
            border: none;
            background: none;
            width: 100%;
            text-align: left;
        }
        
        .menu-item:hover {
            background: #f3f4f6;
            color: #4f46e5;
        }
        
        .menu-item.active {
            background: #eef2ff;
            color: #4f46e5;
            border-right: 3px solid #4f46e5;
        }
        
        .menu-icon {
            width: 20px;
            font-size: 16px;
            text-align: center;
        }
        
        .hot-badge {
            background: #ef4444;
            color: white;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 10px;
            margin-left: auto;
        }
        
        /* 右侧主内容区 */
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #f8fafc;
        }
        
        .content-header {
            background: #fff;
            padding: 20px 30px;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .content-title {
            font-size: 24px;
            font-weight: 600;
            color: #1f2937;
        }
        
        .content-body {
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }
        
        /* 论文写作流程 */
        .workflow-container {
            background: linear-gradient(135deg, #f3e8ff 0%, #e0e7ff 100%);
            border-radius: 16px;
            padding: 40px;
            margin-bottom: 30px;
        }
        
        .workflow-steps {
            display: flex;
            flex-direction: column;
            gap: 20px;
            max-width: 500px;
            margin: 0 auto;
        }
        
        .workflow-step {
            background: rgba(255,255,255,0.9);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            position: relative;
            border: 2px solid transparent;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .workflow-step.active {
            border-color: #4f46e5;
            background: #fff;
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.2);
        }
        
        .workflow-step:not(:last-child)::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-top: 8px solid #6366f1;
        }
        
        .step-title {
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 8px;
        }
        
        .step-desc {
            font-size: 14px;
            color: #6b7280;
        }
        
        .step-number {
            position: absolute;
            top: -10px;
            right: -10px;
            width: 24px;
            height: 24px;
            background: #4f46e5;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }
        
        /* 功能卡片 */
        .feature-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .feature-card {
            background: #fff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .feature-card:hover {
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        
        .card-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            margin-bottom: 16px;
            font-size: 20px;
        }
        
        .card-title {
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 8px;
        }
        
        .card-desc {
            font-size: 14px;
            color: #6b7280;
            line-height: 1.5;
        }
        
        /* 表单样式 */
        .form-container {
            background: #fff;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-top: 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 8px;
        }
        
        .form-input, .form-textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.2s;
        }
        
        .form-input:focus, .form-textarea:focus {
            outline: none;
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        
        .form-textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        .file-upload {
            border: 2px dashed #d1d5db;
            border-radius: 8px;
            padding: 40px 20px;
            text-align: center;
            transition: all 0.2s;
            cursor: pointer;
        }
        
        .file-upload:hover {
            border-color: #4f46e5;
            background: #f9fafb;
        }
        
        .file-upload.dragover {
            border-color: #4f46e5;
            background: #eef2ff;
        }
        
        .upload-icon {
            font-size: 48px;
            color: #9ca3af;
            margin-bottom: 16px;
        }
        
        .upload-text {
            font-size: 16px;
            color: #374151;
            margin-bottom: 8px;
        }
        
        .upload-hint {
            font-size: 14px;
            color: #6b7280;
        }
        
        /* 按钮样式 */
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: #4f46e5;
            color: white;
        }
        
        .btn-primary:hover {
            background: #4338ca;
        }
        
        .btn-secondary {
            background: #f3f4f6;
            color: #374151;
        }
        
        .btn-secondary:hover {
            background: #e5e7eb;
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            .main-container {
                flex-direction: column;
            }
            
            .sidebar {
                width: 100%;
                height: auto;
            }
            
            .workflow-steps {
                padding: 20px;
            }
            
            .feature-cards {
                grid-template-columns: 1fr;
            }
        }
        
        /* 隐藏内容区域 */
        .content-section {
            display: none;
        }
        
        .content-section.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="main-container">
        <!-- 左侧菜单 -->
        <div class="sidebar">
            <div class="sidebar-header">
                <div class="logo">
                    <div class="logo-icon">
                        <i class="fas fa-feather"></i>
                    </div>
                    <div class="logo-text">百考通</div>
                </div>
            </div>
            
            <div class="search-box">
                <div class="search-wrapper">
                    <i class="fas fa-search search-icon"></i>
                    <input type="text" class="search-input" placeholder="订单查询">
                </div>
            </div>
            
            <div class="menu-list">
                <button class="menu-item active" data-section="thesis">
                    <i class="fas fa-graduation-cap menu-icon"></i>
                    <span>毕业论文</span>
                </button>
                
                <button class="menu-item" data-section="reduce">
                    <i class="fas fa-compress-alt menu-icon"></i>
                    <span>降重/降AI</span>
                </button>
                
                <button class="menu-item" data-section="literature">
                    <i class="fas fa-book menu-icon"></i>
                    <span>文献综述</span>
                </button>
                
                <button class="menu-item" data-section="proposal">
                    <i class="fas fa-file-alt menu-icon"></i>
                    <span>开题报告</span>
                </button>
                
                <button class="menu-item" data-section="journal">
                    <i class="fas fa-newspaper menu-icon"></i>
                    <span>期刊论文</span>
                </button>
                
                <button class="menu-item" data-section="special">
                    <i class="fas fa-gift menu-icon"></i>
                    <span>限时特惠</span>
                    <span class="hot-badge">HOT</span>
                </button>
                
                <button class="menu-item" data-section="ppt">
                    <i class="fas fa-presentation menu-icon"></i>
                    <span>PPT</span>
                </button>
                
                <button class="menu-item" data-section="task">
                    <i class="fas fa-tasks menu-icon"></i>
                    <span>任务书</span>
                </button>
                
                <button class="menu-item" data-section="report">
                    <i class="fas fa-chart-line menu-icon"></i>
                    <span>实践报告</span>
                </button>
                
                <button class="menu-item" data-section="analysis">
                    <i class="fas fa-chart-bar menu-icon"></i>
                    <span>数据分析</span>
                </button>
                
                <button class="menu-item" data-section="survey">
                    <i class="fas fa-poll menu-icon"></i>
                    <span>问卷调查</span>
                </button>
            </div>
        </div>
        
        <!-- 右侧主内容 -->
        <div class="main-content">
            <div class="content-header">
                <h1 class="content-title" id="pageTitle">毕业论文</h1>
            </div>
            
            <div class="content-body">
                <!-- 毕业论文模块 -->
                <div id="thesis" class="content-section active">
                    <div class="workflow-container">
                        <div class="workflow-steps">
                            <div class="workflow-step active" data-step="1">
                                <div class="step-number">1</div>
                                <div class="step-title">论文标题</div>
                                <div class="step-desc">设置论文标题与主题</div>
                            </div>
                            <div class="workflow-step" data-step="2">
                                <div class="step-number">2</div>
                                <div class="step-title">参考文献</div>
                                <div class="step-desc">添加并管理参考资料</div>
                            </div>
                            <div class="workflow-step" data-step="3">
                                <div class="step-number">3</div>
                                <div class="step-title">大纲</div>
                                <div class="step-desc">组织论文结构与章节</div>
                            </div>
                            <div class="workflow-step" data-step="4">
                                <div class="step-number">4</div>
                                <div class="step-title">下载</div>
                                <div class="step-desc">导出完成的论文</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-container">
                        <div class="form-group">
                            <label class="form-label">论文标题</label>
                            <input type="text" class="form-input" placeholder="请输入论文标题" id="paperTitle">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">研究领域</label>
                            <select class="form-input" id="researchField">
                                <option value="">请选择研究领域</option>
                                <option value="computer">计算机科学</option>
                                <option value="management">工商管理</option>
                                <option value="education">教育学</option>
                                <option value="economics">经济学</option>
                                <option value="engineering">工程技术</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">学历层次</label>
                            <select class="form-input" id="educationLevel">
                                <option value="">请选择学历层次</option>
                                <option value="bachelor">本科</option>
                                <option value="master">硕士</option>
                                <option value="phd">博士</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">关键词</label>
                            <input type="text" class="form-input" placeholder="请输入关键词，用逗号分隔" id="keywords">
                        </div>
                        
                        <button class="btn btn-primary" onclick="generateThesis()">
                            <i class="fas fa-magic"></i>
                            开始生成论文
                        </button>
                    </div>
                </div>
                
                <!-- 开题报告模块 -->
                <div id="proposal" class="content-section">
                    <div class="feature-cards">
                        <div class="feature-card">
                            <div class="card-icon">
                                <i class="fas fa-upload"></i>
                            </div>
                            <div class="card-title">上传开题报告</div>
                            <div class="card-desc">上传您的开题报告文件，我们将为您提供专业的分析和建议</div>
                        </div>
                        
                        <div class="feature-card">
                            <div class="card-icon">
                                <i class="fas fa-edit"></i>
                            </div>
                            <div class="card-title">智能生成开题</div>
                            <div class="card-desc">基于您的研究方向，自动生成完整的开题报告结构</div>
                        </div>
                        
                        <div class="feature-card">
                            <div class="card-icon">
                                <i class="fas fa-check-circle"></i>
                            </div>
                            <div class="card-title">开题审核助手</div>
                            <div class="card-desc">专业的开题报告审核，提供修改建议和优化方案</div>
                        </div>
                    </div>
                    
                    <div class="form-container">
                        <div class="form-group">
                            <label class="form-label">上传开题报告</label>
                            <div class="file-upload" id="proposalUpload">
                                <div class="upload-icon">
                                    <i class="fas fa-cloud-upload-alt"></i>
                                </div>
                                <div class="upload-text">点击上传或拖拽文件到此处</div>
                                <div class="upload-hint">支持 PDF、Word、TXT 格式，大小不超过 10MB</div>
                                <input type="file" id="proposalFile" style="display: none;" accept=".pdf,.doc,.docx,.txt">
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">研究题目</label>
                            <input type="text" class="form-input" placeholder="请输入研究题目" id="researchTitle">
                        </div>
                        
                        <div class="form-group">
                            <label class="form-label">研究背景与意义</label>
                            <textarea class="form-textarea" placeholder="请描述研究背景与意义" id="researchBackground"></textarea>
                        </div>
                        
                        <button class="btn btn-primary" onclick="processProposal()">
                            <i class="fas fa-cog"></i>
                            处理开题报告
                        </button>
                    </div>
                </div>
                
                <!-- 其他功能模块 -->
                <div id="reduce" class="content-section">
                    <div class="form-container">
                        <h2>降重/降AI</h2>
                        <p>智能降重和AI检测功能正在开发中...</p>
                    </div>
                </div>
                
                <div id="literature" class="content-section">
                    <div class="form-container">
                        <h2>文献综述</h2>
                        <p>文献综述功能正在开发中...</p>
                    </div>
                </div>
                
                <div id="journal" class="content-section">
                    <div class="form-container">
                        <h2>期刊论文</h2>
                        <p>期刊论文功能正在开发中...</p>
                    </div>
                </div>
                
                <div id="special" class="content-section">
                    <div class="form-container">
                        <h2>限时特惠</h2>
                        <p>特惠活动正在开发中...</p>
                    </div>
                </div>
                
                <div id="ppt" class="content-section">
                    <div class="form-container">
                        <h2>PPT</h2>
                        <p>PPT生成功能正在开发中...</p>
                    </div>
                </div>
                
                <div id="task" class="content-section">
                    <div class="form-container">
                        <h2>任务书</h2>
                        <p>任务书功能正在开发中...</p>
                    </div>
                </div>
                
                <div id="report" class="content-section">
                    <div class="form-container">
                        <h2>实践报告</h2>
                        <p>实践报告功能正在开发中...</p>
                    </div>
                </div>
                
                <div id="analysis" class="content-section">
                    <div class="form-container">
                        <h2>数据分析</h2>
                        <p>数据分析功能正在开发中...</p>
                    </div>
                </div>
                
                <div id="survey" class="content-section">
                    <div class="form-container">
                        <h2>问卷调查</h2>
                        <p>问卷调查功能正在开发中...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 菜单切换功能
        const menuItems = document.querySelectorAll('.menu-item');
        const contentSections = document.querySelectorAll('.content-section');
        const pageTitle = document.getElementById('pageTitle');
        
        const sectionTitles = {
            'thesis': '毕业论文',
            'reduce': '降重/降AI', 
            'literature': '文献综述',
            'proposal': '开题报告',
            'journal': '期刊论文',
            'special': '限时特惠',
            'ppt': 'PPT',
            'task': '任务书',
            'report': '实践报告',
            'analysis': '数据分析',
            'survey': '问卷调查'
        };
        
        menuItems.forEach(item => {
            item.addEventListener('click', () => {
                const section = item.getAttribute('data-section');
                
                // 移除所有活跃状态
                menuItems.forEach(mi => mi.classList.remove('active'));
                contentSections.forEach(cs => cs.classList.remove('active'));
                
                // 添加活跃状态
                item.classList.add('active');
                document.getElementById(section).classList.add('active');
                
                // 更新页面标题
                pageTitle.textContent = sectionTitles[section];
            });
        });
        
        // 论文生成流程步骤切换
        const workflowSteps = document.querySelectorAll('.workflow-step');
        workflowSteps.forEach(step => {
            step.addEventListener('click', () => {
                workflowSteps.forEach(s => s.classList.remove('active'));
                step.classList.add('active');
            });
        });
        
        // 文件上传功能
        const proposalUpload = document.getElementById('proposalUpload');
        const proposalFile = document.getElementById('proposalFile');
        
        proposalUpload.addEventListener('click', () => {
            proposalFile.click();
        });
        
        proposalUpload.addEventListener('dragover', (e) => {
            e.preventDefault();
            proposalUpload.classList.add('dragover');
        });
        
        proposalUpload.addEventListener('dragleave', () => {
            proposalUpload.classList.remove('dragover');
        });
        
        proposalUpload.addEventListener('drop', (e) => {
            e.preventDefault();
            proposalUpload.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });
        
        proposalFile.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        });
        
        function handleFileUpload(file) {
            console.log('上传文件:', file.name);
            // 这里可以添加文件上传逻辑
            proposalUpload.innerHTML = \`
                <div class="upload-icon">
                    <i class="fas fa-check-circle" style="color: #10b981;"></i>
                </div>
                <div class="upload-text">\${file.name}</div>
                <div class="upload-hint">文件上传成功</div>
            \`;
        }
        
        // 生成论文功能
        function generateThesis() {
            const title = document.getElementById('paperTitle').value;
            const field = document.getElementById('researchField').value;
            const level = document.getElementById('educationLevel').value;
            const keywords = document.getElementById('keywords').value;
            
            if (!title || !field || !level || !keywords) {
                alert('请填写所有必填信息');
                return;
            }
            
            console.log('生成论文参数:', { title, field, level, keywords });
            
            // 调用后端API
            fetch('/api/paper/generate-title', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    keywords,
                    education_level: level,
                    field
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('论文生成结果:', data);
                alert('论文生成完成！');
            })
            .catch(error => {
                console.error('错误:', error);
                alert('生成论文时发生错误，请稍后重试');
            });
        }
        
        // 处理开题报告
        function processProposal() {
            const title = document.getElementById('researchTitle').value;
            const background = document.getElementById('researchBackground').value;
            
            if (!title || !background) {
                alert('请填写研究题目和背景');
                return;
            }
            
            console.log('处理开题报告:', { title, background });
            alert('开题报告处理完成！');
        }
    </script>
</body>
</html>`);
});

// API routes for file upload
app.post('/upload/proposal', upload.single('proposal'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }
  
  res.json({ 
    success: true, 
    filename: req.file.filename,
    originalName: req.file.originalname,
    path: req.file.path 
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'frontend' });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`前端服务器运行在 http://0.0.0.0:${PORT}`);
});