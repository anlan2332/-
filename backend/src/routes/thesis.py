"""
论文写作相关路由
"""
import os
import json
import openai
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from src.models.database import db, User, Paper, WritingAssistant, APIKey
from src.websocket_manager import notify_paper_progress, ws_manager

thesis_bp = Blueprint('thesis', __name__)

# 您的API密钥和助手指令
DEFAULT_API_KEY = "039c31ba-ebd5-429b-8e88-593eb0e0dc67"
ASSISTANT_INSTRUCTIONS = """1.在保持大意和字数不变或缩减的情况下，拟用学术化的语言重新输出以上内容，减少小开头，少aigc重复率，增强段落衔接感，尽量减少首先、然后、再者、最后等相似词汇的使用次数。
2.以以上文献为我撰写国内外研究，例如学者xx在什么什么方面做了什么什么，然后在其学者名字后面加[]序号
3.根据参考文献撰写，选取几个代表性理论，加入序号引用即可
4.根据文件内容及题目搜索五年内的10篇国内文献.5篇国外文献，要求真实，以gbt2015格式输出
5.根据这个开题报告为我撰写一篇8000字的论文，绪论的国内外研究引用参考文献标注学者和序号，没有用完的参考文献可在正文中引用，同样标注序号；文献引用按照顺序，如果参考文献顺序不对，可以调整参考文献的顺序。引用过的文献就不要再引用了。
跟据以上修改意见修改，并告诉我怎么添加和修改，把需要添加和修改的内容告诉我。
整篇文章用学术化的语言输出，减少小开头，少aigc重复率，增强段落衔接感，尽量减少首先、然后、再者、最后等相似词汇的使用次数。可输出图表，表格正常输出，图片用svg输出。
仔细反复校对是否符合开题，不要自作主张，确保内容正确。
先输出内容，最后输出图片，标记图片引用的地方（如图xx所示）。
参考模板，根据任务书和开题报告，帮我撰写基于Anylogic的城市道路交通拥堵特性分析与仿真字数控制在15000字以内。只在国内外研究中引用参考文献并撰写，加入序号；加入图表，并在文中说明引用。图片选用电气控制图风格，黑白色，非必要不使用彩色。如需引用数据，标注数据来源。
整篇文章用学术化的语言输出，减少小开头，少aigc重复率，增强段落衔接感，尽量减少首先、然后、再者、最后等相似词汇的使用次数，仔细反复校对是否符合开题和任务书以及模板，不要自作主张，确保内容和数据正确。
模仿中国本科生的水平和角度去撰写，降低aigc率，逻辑要严谨，具有研究深度，结构模仿人类，不要太完美。取消首先其次等用语，要用停顿感，尽量减少首先、然后、再者、最后等相似词汇的使用次数，减少小开，头不要一气呵成明白吗。"""

def get_openai_client():
    """获取OpenAI客户端"""
    try:
        # 优先从数据库获取活跃的API密钥
        api_key = APIKey.query.filter_by(service_type='openai', is_active=True).order_by(APIKey.priority).first()
        if api_key:
            return openai.OpenAI(api_key=api_key.api_key, base_url=api_key.api_base)
        else:
            # 使用默认密钥
            return openai.OpenAI(api_key=DEFAULT_API_KEY)
    except Exception as e:
        print(f"获取OpenAI客户端失败: {e}")
        return None

def log_user_activity(user_id: int, action: str, details: dict = None):
    """记录用户活动"""
    try:
        # 暂时使用print记录，后续可扩展为完整的活动日志系统
        print(f"用户 {user_id} 执行操作: {action}, 详情: {details}")
    except Exception as e:
        print(f"记录用户活动失败: {e}")

@thesis_bp.route('/create', methods=['POST'])
def create_thesis():
    """创建新论文"""
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
        title = data.get('title', '').strip()
        field = data.get('field', '').strip()
        education_level = data.get('education_level', '').strip()
        keywords = data.get('keywords', '').strip()
        description = data.get('description', '').strip()
        word_count = data.get('word_count', 8000)
        
        if not title:
            return jsonify({'success': False, 'message': '论文标题不能为空'}), 400
        
        # 创建论文记录
        paper = Paper(
            user_id=user_id,
            title=title,
            paper_type='graduation_thesis',
            status='created',
            config=json.dumps({
                'field': field,
                'education_level': education_level,
                'keywords': keywords,
                'description': description,
                'word_count': word_count
            }, ensure_ascii=False)
        )
        
        db.session.add(paper)
        db.session.commit()
        
        # 记录用户活动
        log_user_activity(user_id, 'create_thesis', {
            'paper_id': paper.id,
            'title': title,
            'field': field
        })
        
        return jsonify({
            'success': True,
            'message': '论文创建成功',
            'data': {
                'paper_id': paper.id,
                'title': title,
                'status': paper.status,
                'created_at': paper.created_at.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建论文失败: {str(e)}'}), 500

@thesis_bp.route('/generate', methods=['POST'])
def generate_thesis():
    """生成论文内容"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        paper_id = data.get('paper_id')
        if not paper_id:
            return jsonify({'success': False, 'message': '论文ID不能为空'}), 400
        
        # 获取论文信息
        paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
        if not paper:
            return jsonify({'success': False, 'message': '论文不存在'}), 404
        
        # 解析论文配置
        config = json.loads(paper.config) if paper.config else {}
        
        # 构建提示词
        prompt = f"""根据以下信息生成高质量的学术论文：

论文标题：{paper.title}
研究领域：{config.get('field', '')}
学历层次：{config.get('education_level', '')}
关键词：{config.get('keywords', '')}
补充说明：{config.get('description', '')}
目标字数：{config.get('word_count', 8000)}字

{ASSISTANT_INSTRUCTIONS}

请按照学术规范生成完整的论文内容，包括：
1. 摘要
2. 关键词
3. 绪论
4. 文献综述
5. 研究方法
6. 结果与分析
7. 结论
8. 参考文献

要求：
- 内容严谨、逻辑清晰
- 符合学术写作规范
- 降低AIGC检测率
- 模仿本科生写作风格
- 包含真实的参考文献引用
"""

        # 更新论文状态
        paper.status = 'generating'
        db.session.commit()
        
        # 发送进度通知
        notify_paper_progress(user_id, paper_id, 10, '开始生成论文...')
        
        # 调用AI生成
        client = get_openai_client()
        if not client:
            paper.status = 'failed'
            db.session.commit()
            return jsonify({'success': False, 'message': 'AI服务暂时不可用'}), 500
        
        try:
            notify_paper_progress(user_id, paper_id, 30, '正在调用AI模型...')
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的学术写作助手，擅长生成高质量的学术论文。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            notify_paper_progress(user_id, paper_id, 80, '正在处理生成结果...')
            
            # 更新论文内容
            paper.content = content
            paper.status = 'completed'
            paper.word_count = len(content)
            db.session.commit()
            
            notify_paper_progress(user_id, paper_id, 100, '论文生成完成！')
            
            # 记录用户活动
            log_user_activity(user_id, 'generate_thesis', {
                'paper_id': paper_id,
                'word_count': len(content)
            })
            
            return jsonify({
                'success': True,
                'message': '论文生成成功',
                'data': {
                    'paper_id': paper_id,
                    'content': content,
                    'word_count': len(content),
                    'status': paper.status
                }
            })
            
        except Exception as e:
            paper.status = 'failed'
            db.session.commit()
            notify_paper_progress(user_id, paper_id, 0, f'生成失败: {str(e)}')
            return jsonify({'success': False, 'message': f'AI生成失败: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成论文失败: {str(e)}'}), 500

@thesis_bp.route('/list', methods=['GET'])
def list_thesis():
    """获取用户论文列表"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        papers = Paper.query.filter_by(user_id=user_id).order_by(Paper.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        paper_list = []
        for paper in papers.items:
            config = json.loads(paper.config) if paper.config else {}
            paper_list.append({
                'id': paper.id,
                'title': paper.title,
                'paper_type': paper.paper_type,
                'status': paper.status,
                'word_count': paper.word_count,
                'field': config.get('field', ''),
                'education_level': config.get('education_level', ''),
                'created_at': paper.created_at.isoformat(),
                'updated_at': paper.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': {
                'papers': paper_list,
                'total': papers.total,
                'pages': papers.pages,
                'current_page': papers.page,
                'per_page': papers.per_page
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取论文列表失败: {str(e)}'}), 500

@thesis_bp.route('/<int:paper_id>', methods=['GET'])
def get_thesis(paper_id):
    """获取论文详情"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
        if not paper:
            return jsonify({'success': False, 'message': '论文不存在'}), 404
        
        config = json.loads(paper.config) if paper.config else {}
        
        return jsonify({
            'success': True,
            'data': {
                'id': paper.id,
                'title': paper.title,
                'paper_type': paper.paper_type,
                'status': paper.status,
                'content': paper.content,
                'word_count': paper.word_count,
                'config': config,
                'created_at': paper.created_at.isoformat(),
                'updated_at': paper.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取论文详情失败: {str(e)}'}), 500

@thesis_bp.route('/<int:paper_id>/update', methods=['PUT'])
def update_thesis(paper_id):
    """更新论文"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
        if not paper:
            return jsonify({'success': False, 'message': '论文不存在'}), 404
        
        data = request.get_json()
        
        # 更新基本信息
        if 'title' in data:
            paper.title = data['title']
        if 'content' in data:
            paper.content = data['content']
            paper.word_count = len(data['content'])
        
        # 更新配置
        if 'config' in data:
            existing_config = json.loads(paper.config) if paper.config else {}
            existing_config.update(data['config'])
            paper.config = json.dumps(existing_config, ensure_ascii=False)
        
        db.session.commit()
        
        # 记录用户活动
        log_user_activity(user_id, 'update_thesis', {
            'paper_id': paper_id,
            'title': paper.title
        })
        
        return jsonify({
            'success': True,
            'message': '论文更新成功',
            'data': {
                'id': paper.id,
                'title': paper.title,
                'status': paper.status,
                'word_count': paper.word_count
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新论文失败: {str(e)}'}), 500

@thesis_bp.route('/<int:paper_id>/delete', methods=['DELETE'])
def delete_thesis(paper_id):
    """删除论文"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
        if not paper:
            return jsonify({'success': False, 'message': '论文不存在'}), 404
        
        # 记录用户活动
        log_user_activity(user_id, 'delete_thesis', {
            'paper_id': paper_id,
            'title': paper.title
        })
        
        db.session.delete(paper)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '论文删除成功'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除论文失败: {str(e)}'}), 500

@thesis_bp.route('/<int:paper_id>/export', methods=['GET'])
def export_thesis(paper_id):
    """导出论文"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
        if not paper:
            return jsonify({'success': False, 'message': '论文不存在'}), 404
        
        if not paper.content:
            return jsonify({'success': False, 'message': '论文内容为空'}), 400
        
        # 记录用户活动
        log_user_activity(user_id, 'export_thesis', {
            'paper_id': paper_id,
            'format': request.args.get('format', 'txt')
        })
        
        export_format = request.args.get('format', 'txt')
        
        if export_format == 'json':
            return jsonify({
                'success': True,
                'data': {
                    'title': paper.title,
                    'content': paper.content,
                    'word_count': paper.word_count,
                    'created_at': paper.created_at.isoformat()
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'filename': f"{paper.title}.txt",
                    'content': paper.content,
                    'size': len(paper.content.encode('utf-8'))
                }
            })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'导出论文失败: {str(e)}'}), 500

@thesis_bp.route('/progress/<int:paper_id>', methods=['GET'])
def get_thesis_progress(paper_id):
    """获取论文生成进度"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        paper = Paper.query.filter_by(id=paper_id, user_id=user_id).first()
        if not paper:
            return jsonify({'success': False, 'message': '论文不存在'}), 404
        
        # 根据状态返回进度
        progress_map = {
            'created': 0,
            'generating': 50,
            'completed': 100,
            'failed': 0
        }
        
        progress = progress_map.get(paper.status, 0)
        
        return jsonify({
            'success': True,
            'data': {
                'paper_id': paper_id,
                'status': paper.status,
                'progress': progress,
                'word_count': paper.word_count
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取进度失败: {str(e)}'}), 500