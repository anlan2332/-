import express from 'express';
import path from 'path';
import cors from 'cors';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = 8080;

// 启用CORS
app.use(cors({
    origin: ['https://5001-i362990uh7vzwuu0d0o9j-6532622b.e2b.dev', '*'],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));

// 设置静态文件服务
app.use(express.static(path.join(__dirname, 'dist')));

// 处理所有路由，返回index.html（用于SPA）
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(port, '0.0.0.0', () => {
    console.log(`百考通AI写作平台前端服务运行在: http://0.0.0.0:${port}`);
    console.log(`访问地址: https://8080-i362990uh7vzwuu0d0o9j-6532622b.e2b.dev`);
});
