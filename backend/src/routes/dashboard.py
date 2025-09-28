from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import random

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """获取仪表板统计数据"""
    try:
        # 模拟数据统计
        stats = {
            'total_papers': random.randint(1000, 5000),
            'today_papers': random.randint(50, 200),
            'total_users': random.randint(500, 2000),
            'active_users': random.randint(100, 500),
            'success_rate': round(random.uniform(85, 95), 1),
            'avg_completion_time': random.randint(30, 120)  # 分钟
        }
        
        return jsonify({
            'success': True,
            'data': stats,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计数据失败: {str(e)}'
        }), 500

@dashboard_bp.route('/paper-trends', methods=['GET'])
def get_paper_trends():
    """获取论文生成趋势数据"""
    try:
        # 生成最近7天的趋势数据
        trends = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            trends.append({
                'date': date,
                'papers': random.randint(20, 100),
                'users': random.randint(10, 50),
                'completion_rate': round(random.uniform(80, 95), 1)
            })
        
        trends.reverse()  # 按日期正序排列
        
        return jsonify({
            'success': True,
            'data': trends,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取趋势数据失败: {str(e)}'
        }), 500

@dashboard_bp.route('/category-distribution', methods=['GET'])
def get_category_distribution():
    """获取论文类别分布数据"""
    try:
        categories = [
            {'name': '毕业论文', 'count': random.randint(200, 500), 'color': '#4f46e5'},
            {'name': '期刊论文', 'count': random.randint(100, 300), 'color': '#7c3aed'},
            {'name': '文献综述', 'count': random.randint(80, 250), 'color': '#06b6d4'},
            {'name': '开题报告', 'count': random.randint(60, 200), 'color': '#10b981'},
            {'name': '实践报告', 'count': random.randint(40, 150), 'color': '#f59e0b'},
            {'name': '任务书', 'count': random.randint(30, 120), 'color': '#ef4444'}
        ]
        
        return jsonify({
            'success': True,
            'data': categories,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取类别分布失败: {str(e)}'
        }), 500

@dashboard_bp.route('/recent-activities', methods=['GET'])
def get_recent_activities():
    """获取最近活动数据"""
    try:
        activities = []
        activity_types = ['论文生成', '文献检索', '开题上传', '降重处理', '格式调整']
        
        for i in range(10):
            activities.append({
                'id': i + 1,
                'type': random.choice(activity_types),
                'user': f'用户{random.randint(1000, 9999)}',
                'status': random.choice(['完成', '处理中', '失败']),
                'time': (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
                'description': f'处理了一份{random.choice(["计算机科学", "工商管理", "教育学", "经济学"])}领域的文档'
            })
        
        return jsonify({
            'success': True,
            'data': activities,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取活动数据失败: {str(e)}'
        }), 500

@dashboard_bp.route('/system-status', methods=['GET'])
def get_system_status():
    """获取系统状态数据"""
    try:
        status = {
            'services': [
                {'name': '论文生成服务', 'status': 'healthy', 'uptime': '99.9%'},
                {'name': '文献检索服务', 'status': 'healthy', 'uptime': '99.8%'},
                {'name': '文件上传服务', 'status': 'healthy', 'uptime': '99.7%'},
                {'name': '数据库服务', 'status': 'healthy', 'uptime': '100%'},
                {'name': 'AI接口服务', 'status': 'healthy', 'uptime': '99.5%'}
            ],
            'server_info': {
                'cpu_usage': round(random.uniform(10, 50), 1),
                'memory_usage': round(random.uniform(30, 70), 1),
                'disk_usage': round(random.uniform(20, 60), 1),
                'network_io': round(random.uniform(5, 25), 1)
            },
            'api_stats': {
                'total_requests': random.randint(5000, 20000),
                'successful_requests': random.randint(4500, 19000),
                'failed_requests': random.randint(100, 500),
                'avg_response_time': round(random.uniform(200, 800), 1)
            }
        }
        
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取系统状态失败: {str(e)}'
        }), 500

@dashboard_bp.route('/export-data', methods=['POST'])
def export_data():
    """导出数据"""
    try:
        data_type = request.json.get('type', 'all')
        date_range = request.json.get('date_range', '7days')
        
        # 模拟数据导出
        export_info = {
            'type': data_type,
            'date_range': date_range,
            'file_name': f'export_{data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            'file_size': f'{random.randint(100, 1000)}KB',
            'download_url': f'/api/dashboard/download/{data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }
        
        return jsonify({
            'success': True,
            'message': '数据导出成功',
            'data': export_info,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'数据导出失败: {str(e)}'
        }), 500

# 新增开题报告处理接口
@dashboard_bp.route('/proposal/upload', methods=['POST'])
def upload_proposal():
    """处理开题报告上传"""
    try:
        # 这里可以处理文件上传逻辑
        data = request.json
        
        title = data.get('title', '')
        background = data.get('background', '')
        
        if not title or not background:
            return jsonify({
                'success': False,
                'message': '请填写完整的研究题目和背景'
            }), 400
        
        # 模拟处理结果
        analysis_result = {
            'title': title,
            'background': background,
            'suggestions': [
                '研究背景描述完整，建议增加更多相关文献支撑',
                '研究题目具有一定的创新性，可以进一步细化研究范围',
                '建议补充研究方法和预期成果的描述'
            ],
            'score': random.randint(75, 95),
            'status': '审核通过',
            'feedback': '您的开题报告整体质量良好，建议根据以上建议进行优化。'
        }
        
        return jsonify({
            'success': True,
            'message': '开题报告处理完成',
            'data': analysis_result,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'处理开题报告失败: {str(e)}'
        }), 500