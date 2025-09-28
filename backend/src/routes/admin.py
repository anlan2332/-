from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
import json
from src.models.database import db, Config, APIKey, WritingAssistant, SystemLog, User, Paper, Order

admin_bp = Blueprint('admin', __name__)

def require_admin():
    """检查管理员权限"""
    user_id = session.get('user_id')
    if not user_id:
        return None, jsonify({
            'success': False,
            'message': '请先登录'
        }), 401
    
    # 简单的管理员验证（实际项目中应该有专门的权限管理）
    admin_users = ['admin', 'administrator', 'root']  # 可以通过配置文件或数据库管理
    username = session.get('username')
    
    if username not in admin_users:
        return None, jsonify({
            'success': False,
            'message': '权限不足'
        }), 403
    
    user = User.query.get(user_id)
    return user, None, None

@admin_bp.route('/dashboard', methods=['GET'])
def admin_dashboard():
    """管理员仪表板"""
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        # 获取系统统计数据
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        vip_users = User.query.filter(User.is_vip == True, User.vip_expire_time > datetime.utcnow()).count()
        
        total_papers = Paper.query.count()
        today_papers = Paper.query.filter(
            Paper.created_at >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        total_orders = Order.query.count()
        paid_orders = Order.query.filter_by(payment_status='paid').count()
        total_revenue = db.session.query(db.func.sum(Order.actual_price)).filter_by(payment_status='paid').scalar() or 0
        
        # 最近7天的趋势数据
        trends = []
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_users = User.query.filter(
                User.created_at >= day_start,
                User.created_at < day_end
            ).count()
            
            day_papers = Paper.query.filter(
                Paper.created_at >= day_start,
                Paper.created_at < day_end
            ).count()
            
            day_revenue = db.session.query(db.func.sum(Order.actual_price)).filter(
                Order.payment_time >= day_start,
                Order.payment_time < day_end,
                Order.payment_status == 'paid'
            ).scalar() or 0
            
            trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'new_users': day_users,
                'new_papers': day_papers,
                'revenue': float(day_revenue)
            })
        
        trends.reverse()
        
        return jsonify({
            'success': True,
            'data': {
                'statistics': {
                    'total_users': total_users,
                    'active_users': active_users,
                    'vip_users': vip_users,
                    'total_papers': total_papers,
                    'today_papers': today_papers,
                    'total_orders': total_orders,
                    'paid_orders': paid_orders,
                    'total_revenue': float(total_revenue)
                },
                'trends': trends
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取管理员仪表板数据失败: {str(e)}'
        }), 500

@admin_bp.route('/configs', methods=['GET'])
def get_configs():
    """获取系统配置列表"""
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        category = request.args.get('category')
        
        query = Config.query
        if category:
            query = query.filter_by(category=category)
        
        configs = query.order_by(Config.category, Config.key).all()
        
        return jsonify({
            'success': True,
            'data': [config.to_dict() for config in configs]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取配置列表失败: {str(e)}'
        }), 500

@admin_bp.route('/configs', methods=['POST'])
def create_config():
    """创建或更新系统配置"""
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        key = data.get('key')
        value = data.get('value')
        description = data.get('description')
        category = data.get('category', 'system')
        
        if not key or value is None:
            return jsonify({
                'success': False,
                'message': '配置键和值不能为空'
            }), 400
        
        config = Config.set_config(key, value, description, category)
        
        # 记录日志
        log = SystemLog(
            user_id=user.id,
            level='INFO',
            category='admin',
            action='update_config',
            message=f'更新配置: {key} = {value}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '配置更新成功',
            'data': config.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新配置失败: {str(e)}'
        }), 500

@admin_bp.route('/api-keys', methods=['GET'])
def get_api_keys():
    """获取API密钥列表"""
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        api_keys = APIKey.query.order_by(APIKey.service_type, APIKey.priority.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [key.to_dict() for key in api_keys]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取API密钥列表失败: {str(e)}'
        }), 500

@admin_bp.route('/api-keys', methods=['POST'])
def create_api_key():
    """创建API密钥"""
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        name = data.get('name')
        service_type = data.get('service_type')
        api_key = data.get('api_key')
        api_base = data.get('api_base')
        priority = data.get('priority', 0)
        
        if not all([name, service_type, api_key]):
            return jsonify({
                'success': False,
                'message': '名称、服务类型和API密钥不能为空'
            }), 400
        
        # 检查是否已存在相同的API密钥
        existing = APIKey.query.filter_by(api_key=api_key).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'API密钥已存在'
            }), 400
        
        api_key_obj = APIKey(
            name=name,
            service_type=service_type,
            api_key=api_key,
            api_base=api_base,
            priority=priority
        )
        
        db.session.add(api_key_obj)
        db.session.commit()
        
        # 记录日志
        log = SystemLog(
            user_id=user.id,
            level='INFO',
            category='admin',
            action='create_api_key',
            message=f'创建API密钥: {name} ({service_type})',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'API密钥创建成功',
            'data': api_key_obj.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'创建API密钥失败: {str(e)}'
        }), 500

@admin_bp.route('/api-keys/<int:key_id>', methods=['PUT'])
def update_api_key(key_id):
    """更新API密钥"""
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        api_key_obj = APIKey.query.get(key_id)
        if not api_key_obj:
            return jsonify({
                'success': False,
                'message': 'API密钥不存在'
            }), 404
        
        data = request.get_json()
        
        if 'name' in data:
            api_key_obj.name = data['name']
        if 'api_key' in data:
            api_key_obj.api_key = data['api_key']
        if 'api_base' in data:
            api_key_obj.api_base = data['api_base']
        if 'priority' in data:
            api_key_obj.priority = data['priority']
        if 'is_active' in data:
            api_key_obj.is_active = data['is_active']
        
        db.session.commit()
        
        # 记录日志
        log = SystemLog(
            user_id=user.id,
            level='INFO',
            category='admin',
            action='update_api_key',
            message=f'更新API密钥: {api_key_obj.name}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'API密钥更新成功',
            'data': api_key_obj.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新API密钥失败: {str(e)}'
        }), 500

@admin_bp.route('/api-keys/<int:key_id>', methods=['DELETE'])
def delete_api_key(key_id):
    """删除API密钥"""
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        api_key_obj = APIKey.query.get(key_id)
        if not api_key_obj:
            return jsonify({
                'success': False,
                'message': 'API密钥不存在'
            }), 404
        
        key_name = api_key_obj.name
        db.session.delete(api_key_obj)
        db.session.commit()
        
        # 记录日志
        log = SystemLog(
            user_id=user.id,
            level='INFO',
            category='admin',
            action='delete_api_key',
            message=f'删除API密钥: {key_name}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'API密钥删除成功'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'删除API密钥失败: {str(e)}'
        }), 500

@admin_bp.route('/writing-assistants', methods=['GET'])
def get_writing_assistants():
    """获取写作助手列表"""
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        assistants = WritingAssistant.query.order_by(
            WritingAssistant.priority.desc(),
            WritingAssistant.created_at.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'data': [assistant.to_dict() for assistant in assistants]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取写作助手列表失败: {str(e)}'
        }), 500

@admin_bp.route('/writing-assistants', methods=['POST'])
def create_writing_assistant():
    """创建写作助手"""
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        prompt_template = data.get('prompt_template')
        model = data.get('model', 'gpt-3.5-turbo')
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2000)
        paper_types = data.get('paper_types', [])
        features = data.get('features', {})
        priority = data.get('priority', 0)
        
        if not all([name, prompt_template]):
            return jsonify({
                'success': False,
                'message': '名称和提示模板不能为空'
            }), 400
        
        assistant = WritingAssistant(
            name=name,
            description=description,
            prompt_template=prompt_template,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            priority=priority
        )
        
        assistant.set_paper_types(paper_types)
        assistant.set_features(features)
        
        db.session.add(assistant)
        db.session.commit()
        
        # 记录日志
        log = SystemLog(
            user_id=user.id,
            level='INFO',
            category='admin',
            action='create_writing_assistant',
            message=f'创建写作助手: {name}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '写作助手创建成功',
            'data': assistant.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'创建写作助手失败: {str(e)}'
        }), 500

@admin_bp.route('/writing-assistants/<int:assistant_id>', methods=['PUT'])
def update_writing_assistant(assistant_id):
    """更新写作助手"""
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        assistant = WritingAssistant.query.get(assistant_id)
        if not assistant:
            return jsonify({
                'success': False,
                'message': '写作助手不存在'
            }), 404
        
        data = request.get_json()
        
        if 'name' in data:
            assistant.name = data['name']
        if 'description' in data:
            assistant.description = data['description']
        if 'prompt_template' in data:
            assistant.prompt_template = data['prompt_template']
        if 'model' in data:
            assistant.model = data['model']
        if 'temperature' in data:
            assistant.temperature = data['temperature']
        if 'max_tokens' in data:
            assistant.max_tokens = data['max_tokens']
        if 'priority' in data:
            assistant.priority = data['priority']
        if 'is_active' in data:
            assistant.is_active = data['is_active']
        if 'paper_types' in data:
            assistant.set_paper_types(data['paper_types'])
        if 'features' in data:
            assistant.set_features(data['features'])
        
        db.session.commit()
        
        # 记录日志
        log = SystemLog(
            user_id=user.id,
            level='INFO',
            category='admin',
            action='update_writing_assistant',
            message=f'更新写作助手: {assistant.name}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '写作助手更新成功',
            'data': assistant.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新写作助手失败: {str(e)}'
        }), 500

@admin_bp.route('/system-logs', methods=['GET'])
def get_system_logs():
    """获取系统日志"""
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        level = request.args.get('level')
        category = request.args.get('category')
        
        query = SystemLog.query
        
        if level:
            query = query.filter_by(level=level)
        if category:
            query = query.filter_by(category=category)
        
        logs = query.order_by(SystemLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'logs': [log.to_dict() for log in logs.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': logs.total,
                    'pages': logs.pages,
                    'has_next': logs.has_next,
                    'has_prev': logs.has_prev
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取系统日志失败: {str(e)}'
        }), 500

@admin_bp.route('/hot-update', methods=['POST'])
def hot_update_config():
    """热更新配置"""
    try:
        user, error_response, status_code = require_admin()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        config_type = data.get('type')  # 'api_keys', 'writing_assistants', 'system_config'
        action = data.get('action')  # 'reload', 'update', 'restart'
        
        # 这里可以实现具体的热更新逻辑
        # 比如重新加载配置、更新缓存、重启服务等
        
        # 记录日志
        log = SystemLog(
            user_id=user.id,
            level='INFO',
            category='admin',
            action='hot_update',
            message=f'执行热更新: {config_type} - {action}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '热更新执行成功'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'热更新失败: {str(e)}'
        }), 500