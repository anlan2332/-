import json
import asyncio
import weakref
from datetime import datetime
from typing import Dict, Set, Any
from flask import session
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from src.models.database import db, Config, APIKey, WritingAssistant, SystemLog

# 全局WebSocket管理器实例
ws_manager = None

class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.connections: Dict[str, Set[str]] = {}  # room -> {session_ids}
        self.user_sessions: Dict[int, Set[str]] = {}  # user_id -> {session_ids}
        
    def add_connection(self, session_id: str, user_id: int = None):
        """添加连接"""
        if user_id:
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = set()
            self.user_sessions[user_id].add(session_id)
    
    def remove_connection(self, session_id: str, user_id: int = None):
        """移除连接"""
        if user_id and user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]
    
    def join_room(self, session_id: str, room: str):
        """加入房间"""
        if room not in self.connections:
            self.connections[room] = set()
        self.connections[room].add(session_id)
    
    def leave_room(self, session_id: str, room: str):
        """离开房间"""
        if room in self.connections:
            self.connections[room].discard(session_id)
            if not self.connections[room]:
                del self.connections[room]
    
    def broadcast_to_room(self, room: str, event: str, data: Any):
        """向房间广播消息"""
        if room in self.connections:
            self.socketio.emit(event, data, room=room)
    
    def broadcast_to_user(self, user_id: int, event: str, data: Any):
        """向特定用户广播消息"""
        if user_id in self.user_sessions:
            for session_id in self.user_sessions[user_id]:
                self.socketio.emit(event, data, room=session_id)
    
    def broadcast_to_admins(self, event: str, data: Any):
        """向管理员广播消息"""
        self.broadcast_to_room('admin', event, data)
    
    def broadcast_config_update(self, config_type: str, config_data: Any):
        """广播配置更新"""
        message = {
            'type': 'config_update',
            'config_type': config_type,
            'data': config_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # 向所有管理员广播
        self.broadcast_to_admins('config_update', message)
        
        # 向前端广播（如果需要）
        self.broadcast_to_room('frontend', 'config_update', message)



def init_websocket(app, socketio: SocketIO):
    """初始化WebSocket"""
    global ws_manager
    ws_manager = WebSocketManager(socketio)
    
    @socketio.on('connect')
    def handle_connect():
        """处理连接"""
        try:
            user_id = session.get('user_id')
            session_id = session.get('session_id', '')
            
            if user_id:
                ws_manager.add_connection(session_id, user_id)
                
                # 管理员自动加入管理房间
                username = session.get('username', '')
                if username in ['admin', 'administrator', 'root']:
                    join_room('admin')
                    ws_manager.join_room(session_id, 'admin')
            
            # 所有连接加入前端房间
            join_room('frontend')
            ws_manager.join_room(session_id, 'frontend')
            
            emit('connected', {
                'message': '连接成功',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            emit('error', {'message': f'连接失败: {str(e)}'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """处理断开连接"""
        try:
            user_id = session.get('user_id')
            session_id = session.get('session_id', '')
            
            if user_id:
                ws_manager.remove_connection(session_id, user_id)
            
            # 离开所有房间
            leave_room('frontend')
            leave_room('admin')
            ws_manager.leave_room(session_id, 'frontend')
            ws_manager.leave_room(session_id, 'admin')
            
        except Exception as e:
            print(f'断开连接处理失败: {e}')
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """加入房间"""
        try:
            room = data.get('room')
            if not room:
                emit('error', {'message': '房间名不能为空'})
                return
            
            # 验证权限
            user_id = session.get('user_id')
            username = session.get('username', '')
            
            if room == 'admin' and username not in ['admin', 'administrator', 'root']:
                emit('error', {'message': '权限不足'})
                return
            
            join_room(room)
            session_id = session.get('session_id', '')
            ws_manager.join_room(session_id, room)
            
            emit('joined_room', {
                'room': room,
                'message': f'已加入房间: {room}',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            emit('error', {'message': f'加入房间失败: {str(e)}'})
    
    @socketio.on('leave_room')
    def handle_leave_room(data):
        """离开房间"""
        try:
            room = data.get('room')
            if room:
                leave_room(room)
                session_id = session.get('session_id', '')
                ws_manager.leave_room(session_id, room)
                
                emit('left_room', {
                    'room': room,
                    'message': f'已离开房间: {room}',
                    'timestamp': datetime.utcnow().isoformat()
                })
        except Exception as e:
            emit('error', {'message': f'离开房间失败: {str(e)}'})
    
    @socketio.on('admin_message')
    def handle_admin_message(data):
        """处理管理员消息"""
        try:
            username = session.get('username', '')
            if username not in ['admin', 'administrator', 'root']:
                emit('error', {'message': '权限不足'})
                return
            
            message_type = data.get('type')
            message_data = data.get('data', {})
            
            if message_type == 'reload_config':
                # 重新加载配置
                reload_system_config()
            elif message_type == 'update_api_keys':
                # 更新API密钥
                broadcast_api_keys_update()
            elif message_type == 'update_writing_assistants':
                # 更新写作助手
                broadcast_writing_assistants_update()
            
            emit('admin_message_sent', {
                'type': message_type,
                'message': '消息发送成功',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            emit('error', {'message': f'发送管理员消息失败: {str(e)}'})
    
    @socketio.on('ping')
    def handle_ping():
        """处理心跳"""
        emit('pong', {'timestamp': datetime.utcnow().isoformat()})

def reload_system_config():
    """重新加载系统配置"""
    try:
        configs = Config.query.all()
        config_data = {config.key: config.value for config in configs}
        
        # 广播配置更新
        if ws_manager:
            ws_manager.broadcast_config_update('system_config', config_data)
        
        return True
    except Exception as e:
        print(f'重新加载系统配置失败: {e}')
        return False

def broadcast_api_keys_update():
    """广播API密钥更新"""
    try:
        api_keys = APIKey.query.filter_by(is_active=True).all()
        
        # 按服务类型组织API密钥
        keys_by_service = {}
        for key in api_keys:
            service = key.service_type
            if service not in keys_by_service:
                keys_by_service[service] = []
            keys_by_service[service].append({
                'id': key.id,
                'name': key.name,
                'api_base': key.api_base,
                'priority': key.priority
                # 不包含实际的API密钥，出于安全考虑
            })
        
        # 广播更新
        if ws_manager:
            ws_manager.broadcast_config_update('api_keys', keys_by_service)
        
        return True
    except Exception as e:
        print(f'广播API密钥更新失败: {e}')
        return False

def broadcast_writing_assistants_update():
    """广播写作助手更新"""
    try:
        assistants = WritingAssistant.query.filter_by(is_active=True).all()
        assistants_data = [assistant.to_dict() for assistant in assistants]
        
        # 广播更新
        if ws_manager:
            ws_manager.broadcast_config_update('writing_assistants', assistants_data)
        
        return True
    except Exception as e:
        print(f'广播写作助手更新失败: {e}')
        return False

def notify_paper_progress(user_id: int, paper_id: int, progress: int, status: str):
    """通知论文生成进度"""
    if ws_manager:
        message = {
            'type': 'paper_progress',
            'paper_id': paper_id,
            'progress': progress,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }
        ws_manager.broadcast_to_user(user_id, 'paper_progress', message)

def notify_system_alert(level: str, message: str, details: dict = None):
    """发送系统警报"""
    if ws_manager:
        alert = {
            'type': 'system_alert',
            'level': level,
            'message': message,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        ws_manager.broadcast_to_admins('system_alert', alert)

def notify_user_action(user_id: int, action: str, data: dict = None):
    """通知用户操作结果"""
    if ws_manager:
        message = {
            'type': 'user_action',
            'action': action,
            'data': data or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        ws_manager.broadcast_to_user(user_id, 'user_action', message)