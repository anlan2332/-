import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, session
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
import uuid
import secrets

# 导入数据库和模型
from src.models.database import db, Config, APIKey, WritingAssistant, User, Paper, Order, SystemLog

# 导入路由
from src.routes.user import user_bp
from src.routes.paper import paper_bp
from src.routes.research import research_bp
from src.routes.dashboard import dashboard_bp
from src.routes.auth import auth_bp
from src.routes.user_center import user_center_bp
from src.routes.admin import admin_bp

# 导入WebSocket管理器
from src.websocket_manager import init_websocket

# 加载环境变量
load_dotenv()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# 配置会话和安全
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24小时

# 启用CORS（支持WebSocket）
CORS(app, origins="*", supports_credentials=True)

# 初始化SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 导入论文路由
from src.routes.thesis import thesis_bp

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(paper_bp, url_prefix='/api/paper')
app.register_blueprint(research_bp, url_prefix='/api/research')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_center_bp, url_prefix='/api/user')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(thesis_bp, url_prefix='/api/thesis')

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 初始化数据库和默认数据
def init_database():
    """初始化数据库和默认数据"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建默认管理员账户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@baikaotong.com',
                real_name='系统管理员',
                balance=0.0,
                points=0,
                is_active=True,
                is_vip=True
            )
            admin_user.set_password('admin123')  # 请在生产环境中修改
            db.session.add(admin_user)
        
        # 创建默认系统配置
        default_configs = [
            ('site_name', '百考通AI写作平台', '网站名称', 'system'),
            ('site_description', '专业的AI学术写作助手平台', '网站描述', 'system'),
            ('default_balance', '10.0', '新用户默认余额', 'user'),
            ('default_points', '100', '新用户默认积分', 'user'),
            ('vip_month_price', '19.9', '月会员价格', 'vip'),
            ('vip_quarter_price', '49.9', '季会员价格', 'vip'),
            ('vip_year_price', '99.9', '年会员价格', 'vip'),
            ('max_paper_length', '50000', '论文最大字数', 'paper'),
            ('max_daily_papers', '10', 'VIP用户每日最大论文数', 'paper'),
            ('enable_websocket', 'true', '启用WebSocket', 'system')
        ]
        
        for key, value, description, category in default_configs:
            if not Config.query.filter_by(key=key).first():
                config = Config(
                    key=key,
                    value=value,
                    description=description,
                    category=category
                )
                db.session.add(config)
        
        # 创建默认API密钥 - 豆包API
        doubao_key = os.getenv('DOUBAO_API_KEY', '039c31ba-ebd5-429b-8e88-593eb0e0dc67')
        if not APIKey.query.filter_by(service_type='doubao').first():
            api_key = APIKey(
                name='用户提供的豆包API密钥',
                service_type='doubao',
                api_key=doubao_key,
                api_base=os.getenv('DOUBAO_API_BASE', 'https://ark.cn-beijing.volces.com/api/v3'),
                priority=1,
                is_active=True
            )
            db.session.add(api_key)
        
        research_key = os.getenv('RESEARCH_API_KEY')
        if research_key and not APIKey.query.filter_by(service_type='research').first():
            api_key = APIKey(
                name='默认研究API密钥',
                service_type='research',
                api_key=research_key,
                api_base=os.getenv('RESEARCH_API_BASE', 'https://api.openai.com/v1'),
                priority=1,
                is_active=True
            )
            db.session.add(api_key)
        
        # 创建默认写作助手
        default_assistants = [
            {
                'name': '学术论文助手',
                'description': '专门用于生成学术论文的AI助手',
                'prompt_template': '''你是一个专业的学术写作助手。请根据以下要求生成高质量的学术论文内容：

标题：{title}
研究领域：{field}
学历层次：{education_level}
关键词：{keywords}

要求：
1. 内容严谨、逻辑清晰
2. 符合学术写作规范
3. 引用相关文献
4. 结构完整，包含摘要、引言、正文、结论等部分
5. 字数控制在合理范围内

请生成论文内容：''',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'max_tokens': 4000,
                'paper_types': ['graduation_thesis', 'journal_paper', 'conference_paper'],
                'features': {
                    'support_outline': True,
                    'support_references': True,
                    'support_format': True,
                    'max_length': 50000
                },
                'is_active': True,
                'priority': 1
            },
            {
                'name': '开题报告助手',
                'description': '专门用于分析和生成开题报告的AI助手',
                'prompt_template': '''你是一个专业的开题报告分析助手。请根据以下内容分析开题报告的质量并提供建议：

研究题目：{title}
研究背景：{background}

请从以下方面进行分析：
1. 研究题目的创新性和可行性
2. 研究背景的完整性和相关性
3. 研究方法的科学性
4. 预期成果的合理性
5. 改进建议

请提供详细的分析和建议：''',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.8,
                'max_tokens': 2000,
                'paper_types': ['proposal'],
                'features': {
                    'support_analysis': True,
                    'support_suggestions': True,
                    'support_scoring': True
                },
                'is_active': True,
                'priority': 2
            }
        ]
        
        for assistant_data in default_assistants:
            if not WritingAssistant.query.filter_by(name=assistant_data['name']).first():
                assistant = WritingAssistant(
                    name=assistant_data['name'],
                    description=assistant_data['description'],
                    prompt_template=assistant_data['prompt_template'],
                    model=assistant_data['model'],
                    temperature=assistant_data['temperature'],
                    max_tokens=assistant_data['max_tokens'],
                    is_active=assistant_data['is_active'],
                    priority=assistant_data['priority']
                )
                assistant.set_paper_types(assistant_data['paper_types'])
                assistant.set_features(assistant_data['features'])
                db.session.add(assistant)
        
        try:
            db.session.commit()
            print("数据库初始化完成")
        except Exception as e:
            db.session.rollback()
            print(f"数据库初始化失败: {e}")

# 初始化数据库
init_database()

# 初始化WebSocket
init_websocket(app, socketio)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return {
        'status': 'healthy',
        'message': '百考通AI写作平台后端运行正常',
        'version': '1.0.0'
    }

# 会话ID生成中间件
@app.before_request
def before_request():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    session.permanent = True

@app.route('/dashboard')
def dashboard():
    """数据可视化仪表板"""
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'dashboard.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Dashboard template not found", 404

@app.route('/admin')
def admin_panel():
    """管理员控制面板"""
    # 检查管理员权限
    username = session.get('username', '')
    if username not in ['admin', 'administrator', 'root']:
        return "权限不足", 403
    
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'admin.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Admin template not found", 404

@app.route('/test')
def test_page():
    """功能测试页面"""
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'test.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Test template not found", 404

if __name__ == '__main__':
    # 使用SocketIO运行应用，使用端口5001避免冲突
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
