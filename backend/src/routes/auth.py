from flask import Blueprint, request, jsonify, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import re
import secrets
import hashlib
from src.models.database import db, User, SystemLog

auth_bp = Blueprint('auth', __name__)

# 简单的限流器（在实际项目中建议使用Redis）
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

def log_user_action(user_id, action, message, level='INFO', details=None):
    """记录用户操作日志"""
    try:
        log = SystemLog(
            user_id=user_id,
            level=level,
            category='user',
            action=action,
            message=message,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:255]
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"记录日志失败: {e}")

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        phone = data.get('phone', '').strip()
        real_name = data.get('real_name', '').strip()
        
        if not all([username, email, password]):
            return jsonify({
                'success': False,
                'message': '用户名、邮箱和密码不能为空'
            }), 400
        
        # 验证用户名长度
        if len(username) < 3 or len(username) > 20:
            return jsonify({
                'success': False,
                'message': '用户名长度应在3-20个字符之间'
            }), 400
        
        # 验证密码强度
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': '密码长度不能少于6个字符'
            }), 400
        
        # 验证邮箱格式
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': '邮箱格式不正确'
            }), 400
        
        # 验证手机号格式（如果提供）
        if phone and not validate_phone(phone):
            return jsonify({
                'success': False,
                'message': '手机号格式不正确'
            }), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            }), 400
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({
                'success': False,
                'message': '邮箱已被注册'
            }), 400
        
        # 检查手机号是否已存在（如果提供）
        if phone and User.query.filter_by(phone=phone).first():
            return jsonify({
                'success': False,
                'message': '手机号已被注册'
            }), 400
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            phone=phone,
            real_name=real_name,
            balance=10.0,  # 新用户赠送10元
            points=100     # 新用户赠送100积分
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # 记录注册日志
        log_user_action(user.id, 'register', f'用户 {username} 注册成功')
        
        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'balance': user.balance,
                'points': user.points
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }), 500

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        login_name = data.get('username', '').strip()  # 可以是用户名或邮箱
        password = data.get('password', '')
        
        if not all([login_name, password]):
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == login_name) | (User.email == login_name)
        ).first()
        
        if not user or not user.check_password(password):
            log_user_action(
                user.id if user else None,
                'login_failed',
                f'登录失败: {login_name}',
                'WARNING'
            )
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': '账户已被禁用，请联系客服'
            }), 403
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 设置会话
        session['user_id'] = user.id
        session['username'] = user.username
        
        # 记录登录日志
        log_user_action(user.id, 'login', f'用户 {user.username} 登录成功')
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': user.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户退出登录"""
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        
        session.clear()
        
        if user_id:
            log_user_action(user_id, 'logout', f'用户 {username} 退出登录')
        
        return jsonify({
            'success': True,
            'message': '退出登录成功'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'退出登录失败: {str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """获取用户信息"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': '请先登录'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户信息失败: {str(e)}'
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """更新用户信息"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': '请先登录'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        data = request.get_json()
        
        # 更新允许修改的字段
        if 'real_name' in data:
            user.real_name = data['real_name'].strip()
        
        if 'phone' in data:
            phone = data['phone'].strip()
            if phone:
                if not validate_phone(phone):
                    return jsonify({
                        'success': False,
                        'message': '手机号格式不正确'
                    }), 400
                
                # 检查手机号是否已被其他用户使用
                existing_user = User.query.filter(
                    User.phone == phone,
                    User.id != user.id
                ).first()
                if existing_user:
                    return jsonify({
                        'success': False,
                        'message': '手机号已被其他用户使用'
                    }), 400
            
            user.phone = phone
        
        db.session.commit()
        
        log_user_action(user.id, 'update_profile', '更新个人资料')
        
        return jsonify({
            'success': True,
            'message': '更新成功',
            'data': user.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """修改密码"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': '请先登录'
            }), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404
        
        data = request.get_json()
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not all([old_password, new_password]):
            return jsonify({
                'success': False,
                'message': '旧密码和新密码不能为空'
            }), 400
        
        # 验证旧密码
        if not user.check_password(old_password):
            log_user_action(user.id, 'change_password_failed', '修改密码失败：旧密码错误', 'WARNING')
            return jsonify({
                'success': False,
                'message': '旧密码错误'
            }), 400
        
        # 验证新密码强度
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': '新密码长度不能少于6个字符'
            }), 400
        
        # 设置新密码
        user.set_password(new_password)
        db.session.commit()
        
        log_user_action(user.id, 'change_password', '修改密码成功')
        
        return jsonify({
            'success': True,
            'message': '密码修改成功'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'修改密码失败: {str(e)}'
        }), 500

@auth_bp.route('/check-session', methods=['GET'])
def check_session():
    """检查登录状态"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'message': '未登录'
            }), 401
        
        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.clear()
            return jsonify({
                'success': False,
                'message': '用户不存在或已被禁用'
            }), 401
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user.id,
                'username': user.username,
                'is_vip': user.is_vip_active(),
                'balance': user.balance,
                'points': user.points
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'检查登录状态失败: {str(e)}'
        }), 500