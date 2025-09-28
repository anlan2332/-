from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import json

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20))
    real_name = db.Column(db.String(50))
    
    # 用户状态
    is_active = db.Column(db.Boolean, default=True)
    is_vip = db.Column(db.Boolean, default=False)
    vip_expire_time = db.Column(db.DateTime)
    
    # 余额和积分
    balance = db.Column(db.Float, default=0.0)
    points = db.Column(db.Integer, default=0)
    
    # 使用统计
    total_papers = db.Column(db.Integer, default=0)
    total_words = db.Column(db.Integer, default=0)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关系
    papers = db.relationship('Paper', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_vip_active(self):
        """检查VIP是否有效"""
        return self.is_vip and self.vip_expire_time and self.vip_expire_time > datetime.utcnow()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'real_name': self.real_name,
            'is_active': self.is_active,
            'is_vip': self.is_vip_active(),
            'vip_expire_time': self.vip_expire_time.isoformat() if self.vip_expire_time else None,
            'balance': self.balance,
            'points': self.points,
            'total_papers': self.total_papers,
            'total_words': self.total_words,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Paper(db.Model):
    """论文模型"""
    __tablename__ = 'papers'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 论文基本信息
    title = db.Column(db.String(200), nullable=False)
    paper_type = db.Column(db.String(50), nullable=False)  # 毕业论文、期刊论文等
    field = db.Column(db.String(100))  # 研究领域
    education_level = db.Column(db.String(50))  # 学历层次
    keywords = db.Column(db.Text)
    
    # 论文内容
    outline = db.Column(db.Text)
    content = db.Column(db.Text)
    references = db.Column(db.Text)
    
    # 生成状态
    status = db.Column(db.String(20), default='draft')  # draft, generating, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100
    
    # 统计信息
    word_count = db.Column(db.Integer, default=0)
    char_count = db.Column(db.Integer, default=0)
    page_count = db.Column(db.Integer, default=0)
    
    # 文件信息
    file_path = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    file_format = db.Column(db.String(10))  # pdf, docx, txt
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'paper_type': self.paper_type,
            'field': self.field,
            'education_level': self.education_level,
            'keywords': self.keywords,
            'status': self.status,
            'progress': self.progress,
            'word_count': self.word_count,
            'char_count': self.char_count,
            'page_count': self.page_count,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_format': self.file_format,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class Order(db.Model):
    """订单模型"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 订单信息
    order_no = db.Column(db.String(32), unique=True, nullable=False)
    product_type = db.Column(db.String(50), nullable=False)  # vip, balance, paper
    product_name = db.Column(db.String(100), nullable=False)
    
    # 价格信息
    original_price = db.Column(db.Float, nullable=False)
    actual_price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    
    # 支付信息
    payment_method = db.Column(db.String(20))  # alipay, wechat, balance
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled, refunded
    payment_time = db.Column(db.DateTime)
    transaction_id = db.Column(db.String(100))
    
    # 订单状态
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled, refunded
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def generate_order_no(cls):
        """生成订单号"""
        import time
        import random
        return f"BKT{int(time.time())}{random.randint(1000, 9999)}"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'order_no': self.order_no,
            'product_type': self.product_type,
            'product_name': self.product_name,
            'original_price': self.original_price,
            'actual_price': self.actual_price,
            'discount': self.discount,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'payment_time': self.payment_time.isoformat() if self.payment_time else None,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Config(db.Model):
    """系统配置模型"""
    __tablename__ = 'configs'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    category = db.Column(db.String(50), default='system')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_config(cls, key, default=None):
        """获取配置值"""
        config = cls.query.filter_by(key=key).first()
        return config.value if config else default
    
    @classmethod
    def set_config(cls, key, value, description=None, category='system'):
        """设置配置值"""
        config = cls.query.filter_by(key=key).first()
        if config:
            config.value = value
            if description:
                config.description = description
        else:
            config = cls(key=key, value=value, description=description, category=category)
            db.session.add(config)
        db.session.commit()
        return config
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'category': self.category,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class APIKey(db.Model):
    """API密钥管理模型"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)  # openai, research, etc.
    api_key = db.Column(db.String(255), nullable=False)
    api_base = db.Column(db.String(255))
    
    # 使用统计
    usage_count = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime)
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)  # 优先级，数字越大优先级越高
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_active_key(cls, service_type):
        """获取激活的API密钥"""
        return cls.query.filter_by(
            service_type=service_type, 
            is_active=True
        ).order_by(cls.priority.desc()).first()
    
    def increment_usage(self):
        """增加使用计数"""
        self.usage_count += 1
        self.last_used = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'service_type': self.service_type,
            'api_key': self.api_key[:10] + '...' if self.api_key else None,  # 隐藏部分密钥
            'api_base': self.api_base,
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'is_active': self.is_active,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class WritingAssistant(db.Model):
    """写作助手配置模型"""
    __tablename__ = 'writing_assistants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # 助手配置
    prompt_template = db.Column(db.Text, nullable=False)
    model = db.Column(db.String(50), default='gpt-3.5-turbo')
    temperature = db.Column(db.Float, default=0.7)
    max_tokens = db.Column(db.Integer, default=2000)
    
    # 功能配置
    paper_types = db.Column(db.Text)  # JSON格式存储支持的论文类型
    features = db.Column(db.Text)  # JSON格式存储功能配置
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_paper_types(self):
        """获取支持的论文类型"""
        try:
            return json.loads(self.paper_types) if self.paper_types else []
        except:
            return []
    
    def set_paper_types(self, types):
        """设置支持的论文类型"""
        self.paper_types = json.dumps(types)
    
    def get_features(self):
        """获取功能配置"""
        try:
            return json.loads(self.features) if self.features else {}
        except:
            return {}
    
    def set_features(self, features):
        """设置功能配置"""
        self.features = json.dumps(features)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'prompt_template': self.prompt_template,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'paper_types': self.get_paper_types(),
            'features': self.get_features(),
            'is_active': self.is_active,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SystemLog(db.Model):
    """系统日志模型"""
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    level = db.Column(db.String(20), nullable=False)  # INFO, WARNING, ERROR
    category = db.Column(db.String(50), nullable=False)  # paper, user, payment, system
    action = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text)
    details = db.Column(db.Text)  # JSON格式存储详细信息
    
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'level': self.level,
            'category': self.category,
            'action': self.action,
            'message': self.message,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat()
        }