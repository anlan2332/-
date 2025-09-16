"""
订单管理相关路由
"""
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from src.models.database import db, User, Paper, Order

order_bp = Blueprint('order', __name__)

@order_bp.route('/create', methods=['POST'])
def create_order():
    """创建订单"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 获取用户信息
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 验证输入
        product_type = data.get('product_type', '').strip()
        product_name = data.get('product_name', '').strip()
        original_price = data.get('original_price', 0)
        actual_price = data.get('actual_price', 0)
        
        if not product_type or not product_name:
            return jsonify({'success': False, 'message': '产品类型和名称不能为空'}), 400
        
        if original_price < 0 or actual_price < 0:
            return jsonify({'success': False, 'message': '价格不能为负数'}), 400
        
        # 创建订单记录
        order = Order(
            user_id=user_id,
            order_no=Order.generate_order_no(),
            product_type=product_type,
            product_name=product_name,
            original_price=original_price,
            actual_price=actual_price,
            discount=original_price - actual_price,
            payment_status='pending',
            status='pending'
        )
        
        db.session.add(order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '订单创建成功',
            'data': {
                'id': order.id,
                'order_no': order.order_no,
                'product_type': order.product_type,
                'product_name': order.product_name,
                'original_price': order.original_price,
                'actual_price': order.actual_price,
                'status': order.status,
                'created_at': order.created_at.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建订单失败: {str(e)}'}), 500

@order_bp.route('/<int:order_id>/update', methods=['PUT'])
def update_order(order_id):
    """更新订单状态"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'}), 404
        
        data = request.get_json()
        
        # 更新订单状态
        if 'status' in data:
            order.status = data['status']
            if data['status'] == 'completed':
                order.payment_status = 'paid'
                order.payment_time = datetime.utcnow()
        
        # 更新支付状态
        if 'payment_status' in data:
            order.payment_status = data['payment_status']
            if data['payment_status'] == 'paid':
                order.payment_time = datetime.utcnow()
        
        # 更新支付方式
        if 'payment_method' in data:
            order.payment_method = data['payment_method']
        
        # 更新交易ID
        if 'transaction_id' in data:
            order.transaction_id = data['transaction_id']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '订单更新成功',
            'data': order.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新订单失败: {str(e)}'}), 500

@order_bp.route('/list', methods=['GET'])
def list_orders():
    """获取用户订单列表"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', '')
        
        query = Order.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        order_list = []
        for order in orders.items:
            order_dict = order.to_dict()
            
            # 如果是论文订单，尝试获取关联的论文信息
            if order.product_type == 'paper':
                paper = Paper.query.filter_by(user_id=user_id).filter(
                    Paper.created_at >= order.created_at
                ).first()
                if paper:
                    order_dict['paper_info'] = {
                        'id': paper.id,
                        'title': paper.title,
                        'status': paper.status,
                        'word_count': paper.word_count
                    }
            
            order_list.append(order_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'orders': order_list,
                'total': orders.total,
                'pages': orders.pages,
                'current_page': orders.page,
                'per_page': orders.per_page
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取订单列表失败: {str(e)}'}), 500

@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """获取订单详情"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'}), 404
        
        order_dict = order.to_dict()
        
        # 如果是论文订单，获取关联的论文信息
        if order.product_type == 'paper':
            paper = Paper.query.filter_by(user_id=user_id).filter(
                Paper.created_at >= order.created_at
            ).first()
            if paper:
                order_dict['paper_info'] = {
                    'id': paper.id,
                    'title': paper.title,
                    'status': paper.status,
                    'content': paper.content,
                    'word_count': paper.word_count,
                    'created_at': paper.created_at.isoformat()
                }
        
        return jsonify({
            'success': True,
            'data': order_dict
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取订单详情失败: {str(e)}'}), 500

@order_bp.route('/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """取消订单"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'}), 404
        
        # 只能取消待处理的订单
        if order.status != 'pending':
            return jsonify({'success': False, 'message': '只能取消待处理的订单'}), 400
        
        order.status = 'cancelled'
        order.payment_status = 'cancelled'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '订单已取消',
            'data': order.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'取消订单失败: {str(e)}'}), 500

@order_bp.route('/statistics', methods=['GET'])
def get_order_statistics():
    """获取订单统计信息"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 统计各状态订单数量
        total_orders = Order.query.filter_by(user_id=user_id).count()
        pending_orders = Order.query.filter_by(user_id=user_id, status='pending').count()
        completed_orders = Order.query.filter_by(user_id=user_id, status='completed').count()
        cancelled_orders = Order.query.filter_by(user_id=user_id, status='cancelled').count()
        
        # 计算总消费金额
        total_spent = db.session.query(db.func.sum(Order.actual_price)).filter_by(
            user_id=user_id, 
            payment_status='paid'
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders,
                'cancelled_orders': cancelled_orders,
                'total_spent': float(total_spent)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取统计信息失败: {str(e)}'}), 500