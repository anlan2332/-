from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
import uuid
import random
from src.models.database import db, User, Order, Paper, SystemLog

user_center_bp = Blueprint('user_center', __name__)

def require_login():
    """检查登录状态装饰器"""
    user_id = session.get('user_id')
    if not user_id:
        return None, jsonify({
            'success': False,
            'message': '请先登录'
        }), 401
    
    user = User.query.get(user_id)
    if not user or not user.is_active:
        session.clear()
        return None, jsonify({
            'success': False,
            'message': '用户不存在或已被禁用'
        }), 401
    
    return user, None, None

@user_center_bp.route('/dashboard', methods=['GET'])
def user_dashboard():
    """用户仪表板数据"""
    try:
        user, error_response, status_code = require_login()
        if error_response:
            return error_response, status_code
        
        # 获取用户统计数据
        total_papers = Paper.query.filter_by(user_id=user.id).count()
        completed_papers = Paper.query.filter_by(user_id=user.id, status='completed').count()
        
        # 获取最近的论文
        recent_papers = Paper.query.filter_by(user_id=user.id).order_by(
            Paper.created_at.desc()
        ).limit(5).all()
        
        # 获取最近的订单
        recent_orders = Order.query.filter_by(user_id=user.id).order_by(
            Order.created_at.desc()
        ).limit(5).all()
        
        # 计算本月使用情况
        current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_papers = Paper.query.filter(
            Paper.user_id == user.id,
            Paper.created_at >= current_month
        ).count()
        
        dashboard_data = {
            'user_info': user.to_dict(),
            'statistics': {
                'total_papers': total_papers,
                'completed_papers': completed_papers,
                'monthly_papers': monthly_papers,
                'success_rate': round((completed_papers / total_papers * 100) if total_papers > 0 else 0, 1),
                'total_words': user.total_words,
                'vip_status': user.is_vip_active(),
                'vip_expire': user.vip_expire_time.isoformat() if user.vip_expire_time else None
            },
            'recent_papers': [paper.to_dict() for paper in recent_papers],
            'recent_orders': [order.to_dict() for order in recent_orders]
        }
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取仪表板数据失败: {str(e)}'
        }), 500

@user_center_bp.route('/papers', methods=['GET'])
def user_papers():
    """获取用户论文列表"""
    try:
        user, error_response, status_code = require_login()
        if error_response:
            return error_response, status_code
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status')
        paper_type_filter = request.args.get('type')
        
        # 构建查询
        query = Paper.query.filter_by(user_id=user.id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        if paper_type_filter:
            query = query.filter_by(paper_type=paper_type_filter)
        
        # 分页查询
        papers = query.order_by(Paper.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'papers': [paper.to_dict() for paper in papers.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': papers.total,
                    'pages': papers.pages,
                    'has_next': papers.has_next,
                    'has_prev': papers.has_prev
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取论文列表失败: {str(e)}'
        }), 500

@user_center_bp.route('/orders', methods=['GET'])
def user_orders():
    """获取用户订单列表"""
    try:
        user, error_response, status_code = require_login()
        if error_response:
            return error_response, status_code
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status')
        
        # 构建查询
        query = Order.query.filter_by(user_id=user.id)
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        # 分页查询
        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'orders': [order.to_dict() for order in orders.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': orders.total,
                    'pages': orders.pages,
                    'has_next': orders.has_next,
                    'has_prev': orders.has_prev
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取订单列表失败: {str(e)}'
        }), 500

@user_center_bp.route('/recharge', methods=['POST'])
def create_recharge_order():
    """创建充值订单"""
    try:
        user, error_response, status_code = require_login()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        amount = data.get('amount', 0)
        payment_method = data.get('payment_method', 'alipay')
        
        # 验证充值金额
        if not amount or amount <= 0:
            return jsonify({
                'success': False,
                'message': '充值金额必须大于0'
            }), 400
        
        if amount > 10000:
            return jsonify({
                'success': False,
                'message': '单次充值金额不能超过10000元'
            }), 400
        
        # 创建充值订单
        order = Order(
            user_id=user.id,
            order_no=Order.generate_order_no(),
            product_type='balance',
            product_name=f'账户充值 {amount}元',
            original_price=amount,
            actual_price=amount,
            payment_method=payment_method
        )
        
        db.session.add(order)
        db.session.commit()
        
        # 记录日志
        log = SystemLog(
            user_id=user.id,
            level='INFO',
            category='payment',
            action='create_recharge_order',
            message=f'创建充值订单: {order.order_no}, 金额: {amount}元',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        # 模拟支付（实际项目中需要调用支付接口）
        return jsonify({
            'success': True,
            'message': '订单创建成功',
            'data': {
                'order_no': order.order_no,
                'amount': amount,
                'payment_method': payment_method,
                'payment_url': f'/payment/{order.order_no}',  # 模拟支付URL
                'qr_code': f'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=pay:{order.order_no}'  # 模拟二维码
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'创建充值订单失败: {str(e)}'
        }), 500

@user_center_bp.route('/vip/packages', methods=['GET'])
def vip_packages():
    """获取VIP套餐列表"""
    try:
        packages = [
            {
                'id': 'vip_month',
                'name': '月会员',
                'duration': 30,
                'original_price': 29.9,
                'current_price': 19.9,
                'discount': 33,
                'features': [
                    '无限论文生成',
                    '优先客服支持',
                    '高级模板库',
                    '批量下载',
                    '去除水印'
                ],
                'popular': False
            },
            {
                'id': 'vip_quarter',
                'name': '季度会员',
                'duration': 90,
                'original_price': 89.7,
                'current_price': 49.9,
                'discount': 44,
                'features': [
                    '月会员全部功能',
                    '专属客服',
                    '定制化服务',
                    'AI写作指导',
                    '论文查重'
                ],
                'popular': True
            },
            {
                'id': 'vip_year',
                'name': '年度会员',
                'duration': 365,
                'original_price': 358.8,
                'current_price': 99.9,
                'discount': 72,
                'features': [
                    '季度会员全部功能',
                    '一对一指导',
                    '无限云存储',
                    '数据导出',
                    'API接口'
                ],
                'popular': False
            }
        ]
        
        return jsonify({
            'success': True,
            'data': packages
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取VIP套餐失败: {str(e)}'
        }), 500

@user_center_bp.route('/vip/purchase', methods=['POST'])
def purchase_vip():
    """购买VIP"""
    try:
        user, error_response, status_code = require_login()
        if error_response:
            return error_response, status_code
        
        data = request.get_json()
        package_id = data.get('package_id')
        payment_method = data.get('payment_method', 'balance')
        
        # 获取套餐信息
        packages = {
            'vip_month': {'name': '月会员', 'duration': 30, 'price': 19.9},
            'vip_quarter': {'name': '季度会员', 'duration': 90, 'price': 49.9},
            'vip_year': {'name': '年度会员', 'duration': 365, 'price': 99.9}
        }
        
        package = packages.get(package_id)
        if not package:
            return jsonify({
                'success': False,
                'message': '套餐不存在'
            }), 400
        
        # 如果使用余额支付，检查余额是否足够
        if payment_method == 'balance':
            if user.balance < package['price']:
                return jsonify({
                    'success': False,
                    'message': f'余额不足，当前余额: {user.balance}元'
                }), 400
        
        # 创建VIP订单
        order = Order(
            user_id=user.id,
            order_no=Order.generate_order_no(),
            product_type='vip',
            product_name=package['name'],
            original_price=package['price'],
            actual_price=package['price'],
            payment_method=payment_method,
            status='completed' if payment_method == 'balance' else 'pending',
            payment_status='paid' if payment_method == 'balance' else 'pending',
            payment_time=datetime.utcnow() if payment_method == 'balance' else None
        )
        
        db.session.add(order)
        
        # 如果使用余额支付，直接开通VIP
        if payment_method == 'balance':
            user.balance -= package['price']
            
            # 计算VIP到期时间
            if user.is_vip_active():
                # 如果已经是VIP，延长时间
                expire_time = user.vip_expire_time + timedelta(days=package['duration'])
            else:
                # 如果不是VIP，从现在开始计算
                expire_time = datetime.utcnow() + timedelta(days=package['duration'])
            
            user.is_vip = True
            user.vip_expire_time = expire_time
        
        db.session.commit()
        
        # 记录日志
        log = SystemLog(
            user_id=user.id,
            level='INFO',
            category='payment',
            action='purchase_vip',
            message=f'购买VIP: {package["name"]}, 订单号: {order.order_no}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        if payment_method == 'balance':
            return jsonify({
                'success': True,
                'message': 'VIP开通成功',
                'data': {
                    'order_no': order.order_no,
                    'vip_expire_time': user.vip_expire_time.isoformat(),
                    'remaining_balance': user.balance
                }
            })
        else:
            return jsonify({
                'success': True,
                'message': '订单创建成功',
                'data': {
                    'order_no': order.order_no,
                    'payment_url': f'/payment/{order.order_no}',
                    'qr_code': f'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=vip:{order.order_no}'
                }
            })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'购买VIP失败: {str(e)}'
        }), 500

@user_center_bp.route('/payment/simulate/<order_no>', methods=['POST'])
def simulate_payment(order_no):
    """模拟支付回调（仅用于演示）"""
    try:
        order = Order.query.filter_by(order_no=order_no).first()
        if not order:
            return jsonify({
                'success': False,
                'message': '订单不存在'
            }), 404
        
        if order.payment_status == 'paid':
            return jsonify({
                'success': False,
                'message': '订单已支付'
            }), 400
        
        # 模拟支付成功
        order.payment_status = 'paid'
        order.status = 'completed'
        order.payment_time = datetime.utcnow()
        order.transaction_id = f'txn_{random.randint(100000, 999999)}'
        
        user = User.query.get(order.user_id)
        
        if order.product_type == 'balance':
            # 充值余额
            user.balance += order.actual_price
        elif order.product_type == 'vip':
            # 开通VIP
            duration_map = {
                '月会员': 30,
                '季度会员': 90,
                '年度会员': 365
            }
            duration = duration_map.get(order.product_name, 30)
            
            if user.is_vip_active():
                expire_time = user.vip_expire_time + timedelta(days=duration)
            else:
                expire_time = datetime.utcnow() + timedelta(days=duration)
            
            user.is_vip = True
            user.vip_expire_time = expire_time
        
        db.session.commit()
        
        # 记录日志
        log = SystemLog(
            user_id=user.id,
            level='INFO',
            category='payment',
            action='payment_success',
            message=f'支付成功: {order.order_no}, 金额: {order.actual_price}元',
            details=f'{{"transaction_id": "{order.transaction_id}", "product_type": "{order.product_type}"}}'
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '支付成功',
            'data': {
                'order_no': order.order_no,
                'transaction_id': order.transaction_id
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'支付处理失败: {str(e)}'
        }), 500

@user_center_bp.route('/statistics', methods=['GET'])
def user_statistics():
    """获取用户统计数据"""
    try:
        user, error_response, status_code = require_login()
        if error_response:
            return error_response, status_code
        
        # 按月统计论文生成数量
        monthly_stats = db.session.execute("""
            SELECT 
                strftime('%Y-%m', created_at) as month,
                COUNT(*) as count,
                SUM(word_count) as total_words
            FROM papers 
            WHERE user_id = :user_id 
                AND created_at >= date('now', '-12 months')
            GROUP BY month
            ORDER BY month
        """, {'user_id': user.id}).fetchall()
        
        # 按类型统计论文
        type_stats = db.session.execute("""
            SELECT 
                paper_type,
                COUNT(*) as count,
                AVG(word_count) as avg_words
            FROM papers 
            WHERE user_id = :user_id
            GROUP BY paper_type
        """, {'user_id': user.id}).fetchall()
        
        return jsonify({
            'success': True,
            'data': {
                'monthly_stats': [
                    {
                        'month': row.month,
                        'count': row.count,
                        'total_words': row.total_words or 0
                    } for row in monthly_stats
                ],
                'type_stats': [
                    {
                        'type': row.paper_type,
                        'count': row.count,
                        'avg_words': round(row.avg_words or 0)
                    } for row in type_stats
                ]
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计数据失败: {str(e)}'
        }), 500