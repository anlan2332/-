from flask import Blueprint, request, jsonify, session, render_template_string
from datetime import datetime, timedelta
from src.models.database import db, User, Order, Paper, SystemLog, Config, APIKey
from sqlalchemy import func, desc

admin_panel_bp = Blueprint('admin_panel', __name__)

def require_admin():
    """检查管理员权限"""
    username = session.get('username', '')
    if username not in ['admin', 'administrator', 'root']:
        return False
    return True

# HTML模板
ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>百考通AI写作平台 - 管理后台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-title { font-size: 14px; color: #666; margin-bottom: 8px; }
        .stat-value { font-size: 24px; font-weight: bold; color: #333; }
        .stat-change { font-size: 12px; margin-top: 4px; }
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        .table-container { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .table { width: 100%; border-collapse: collapse; }
        .table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }
        .table th { background: #f9fafb; font-weight: 600; color: #374151; }
        .table tr:hover { background: #f9fafb; }
        .status { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
        .status.active { background: #d1fae5; color: #065f46; }
        .status.inactive { background: #fee2e2; color: #991b1b; }
        .status.completed { background: #dbeafe; color: #1e40af; }
        .status.pending { background: #fef3c7; color: #92400e; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-primary { background: #3b82f6; color: white; }
        .btn-danger { background: #ef4444; color: white; }
        .section { margin-bottom: 40px; }
        .section-title { font-size: 18px; font-weight: 600; margin-bottom: 16px; color: #1f2937; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="font-size: 28px; font-weight: 700; color: #1f2937;">百考通AI写作平台 - 管理后台</h1>
            <p style="color: #6b7280; margin-top: 8px;">欢迎使用后台管理系统</p>
        </div>

        <!-- 统计数据 -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">总用户数</div>
                <div class="stat-value">{{ stats.total_users }}</div>
                <div class="stat-change positive">↗ +{{ stats.new_users_today }} 今日新增</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">总订单数</div>
                <div class="stat-value">{{ stats.total_orders }}</div>
                <div class="stat-change positive">↗ +{{ stats.orders_today }} 今日新增</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">总论文数</div>
                <div class="stat-value">{{ stats.total_papers }}</div>
                <div class="stat-change positive">↗ +{{ stats.papers_today }} 今日新增</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">总收入</div>
                <div class="stat-value">¥{{ "%.2f"|format(stats.total_revenue) }}</div>
                <div class="stat-change positive">↗ +¥{{ "%.2f"|format(stats.revenue_today) }} 今日收入</div>
            </div>
        </div>

        <!-- 最新用户 -->
        <div class="section">
            <div class="section-title">最新注册用户</div>
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>用户ID</th>
                            <th>用户名</th>
                            <th>邮箱</th>
                            <th>注册时间</th>
                            <th>VIP状态</th>
                            <th>余额</th>
                            <th>状态</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user in recent_users %}
                        <tr>
                            <td>{{ user.id }}</td>
                            <td>{{ user.username }}</td>
                            <td>{{ user.email }}</td>
                            <td>{{ user.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                            <td>
                                <span class="status {{ 'active' if user.is_vip else 'inactive' }}">
                                    {{ 'VIP会员' if user.is_vip else '普通用户' }}
                                </span>
                            </td>
                            <td>¥{{ "%.2f"|format(user.balance) }}</td>
                            <td>
                                <span class="status {{ 'active' if user.is_active else 'inactive' }}">
                                    {{ '正常' if user.is_active else '禁用' }}
                                </span>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 最新订单 -->
        <div class="section">
            <div class="section-title">最新订单</div>
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>订单号</th>
                            <th>用户</th>
                            <th>商品</th>
                            <th>金额</th>
                            <th>支付方式</th>
                            <th>状态</th>
                            <th>创建时间</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for order in recent_orders %}
                        <tr>
                            <td>{{ order.order_no }}</td>
                            <td>{{ order.user.username if order.user else '-' }}</td>
                            <td>{{ order.product_name }}</td>
                            <td>¥{{ "%.2f"|format(order.actual_price) }}</td>
                            <td>{{ {'balance': '余额', 'alipay': '支付宝', 'wechat': '微信'}.get(order.payment_method, order.payment_method) }}</td>
                            <td>
                                <span class="status {{ order.status }}">
                                    {{ {'pending': '待处理', 'completed': '已完成', 'cancelled': '已取消'}.get(order.status, order.status) }}
                                </span>
                            </td>
                            <td>{{ order.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 系统日志 -->
        <div class="section">
            <div class="section-title">系统日志</div>
            <div class="table-container">
                <table class="table">
                    <thead>
                        <tr>
                            <th>时间</th>
                            <th>用户</th>
                            <th>级别</th>
                            <th>分类</th>
                            <th>操作</th>
                            <th>消息</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for log in recent_logs %}
                        <tr>
                            <td>{{ log.created_at.strftime('%m-%d %H:%M') }}</td>
                            <td>{{ log.user.username if log.user else '-' }}</td>
                            <td>
                                <span class="status {{ 'active' if log.level == 'INFO' else 'pending' if log.level == 'WARNING' else 'inactive' }}">
                                    {{ log.level }}
                                </span>
                            </td>
                            <td>{{ log.category }}</td>
                            <td>{{ log.action }}</td>
                            <td>{{ log.message[:50] }}{{ '...' if log.message|length > 50 else '' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div style="text-align: center; padding: 20px; color: #6b7280;">
            <p>百考通AI写作平台管理后台 © 2024</p>
        </div>
    </div>
</body>
</html>
'''

@admin_panel_bp.route('/', methods=['GET'])
def admin_dashboard():
    """管理员后台首页"""
    if not require_admin():
        return "权限不足，请先以管理员身份登录", 403
    
    try:
        # 获取统计数据
        today = datetime.now().date()
        
        # 用户统计
        total_users = User.query.count()
        new_users_today = User.query.filter(
            func.date(User.created_at) == today
        ).count()
        
        # 订单统计
        total_orders = Order.query.count()
        orders_today = Order.query.filter(
            func.date(Order.created_at) == today
        ).count()
        
        # 论文统计
        total_papers = Paper.query.count()
        papers_today = Paper.query.filter(
            func.date(Paper.created_at) == today
        ).count()
        
        # 收入统计
        total_revenue = db.session.query(
            func.sum(Order.actual_price)
        ).filter(Order.payment_status == 'paid').scalar() or 0
        
        revenue_today = db.session.query(
            func.sum(Order.actual_price)
        ).filter(
            Order.payment_status == 'paid',
            func.date(Order.created_at) == today
        ).scalar() or 0
        
        # 最新用户
        recent_users = User.query.order_by(desc(User.created_at)).limit(10).all()
        
        # 最新订单
        recent_orders = Order.query.order_by(desc(Order.created_at)).limit(10).all()
        
        # 系统日志
        recent_logs = SystemLog.query.order_by(desc(SystemLog.created_at)).limit(20).all()
        
        stats = {
            'total_users': total_users,
            'new_users_today': new_users_today,
            'total_orders': total_orders,
            'orders_today': orders_today,
            'total_papers': total_papers,
            'papers_today': papers_today,
            'total_revenue': total_revenue,
            'revenue_today': revenue_today
        }
        
        return render_template_string(
            ADMIN_TEMPLATE,
            stats=stats,
            recent_users=recent_users,
            recent_orders=recent_orders,
            recent_logs=recent_logs
        )
    
    except Exception as e:
        return f"获取管理后台数据失败: {str(e)}", 500

@admin_panel_bp.route('/api/stats', methods=['GET'])
def api_stats():
    """API接口获取统计数据"""
    if not require_admin():
        return jsonify({'success': False, 'message': '权限不足'}), 403
    
    try:
        today = datetime.now().date()
        
        stats = {
            'users': {
                'total': User.query.count(),
                'active': User.query.filter_by(is_active=True).count(),
                'vip': User.query.filter_by(is_vip=True).count(),
                'today': User.query.filter(func.date(User.created_at) == today).count()
            },
            'orders': {
                'total': Order.query.count(),
                'completed': Order.query.filter_by(status='completed').count(),
                'pending': Order.query.filter_by(status='pending').count(),
                'today': Order.query.filter(func.date(Order.created_at) == today).count()
            },
            'revenue': {
                'total': db.session.query(func.sum(Order.actual_price)).filter(Order.payment_status == 'paid').scalar() or 0,
                'today': db.session.query(func.sum(Order.actual_price)).filter(
                    Order.payment_status == 'paid',
                    func.date(Order.created_at) == today
                ).scalar() or 0
            }
        }
        
        return jsonify({
            'success': True,
            'data': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计数据失败: {str(e)}'
        }), 500