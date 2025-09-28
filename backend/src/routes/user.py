from flask import Blueprint, jsonify, request
from src.models.user import User, db
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    """获取用户列表"""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': [{'id': u.id, 'username': u.username, 'email': u.email} for u in users],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户列表失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@user_bp.route('/users', methods=['POST'])
def create_user():
    """创建用户"""
    try:
        data = request.get_json()
        user = User(username=data['username'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户创建成功',
            'data': {'id': user.id, 'username': user.username, 'email': user.email},
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建用户失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500