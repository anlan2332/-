"""
开题报告相关路由
"""
import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from src.models.database import db, User
from src.utils.doubao_client import get_doubao_client

proposal_bp = Blueprint('proposal', __name__)

# 允许的文件类型
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'md'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_doubao_api_client():
    """获取豆包API客户端"""
    try:
        return get_doubao_client("039c31ba-ebd5-429b-8e88-593eb0e0dc67")
    except Exception as e:
        print(f"获取豆包API客户端失败: {e}")
        return None

@proposal_bp.route('/upload', methods=['POST'])
def upload_proposal():
    """上传开题报告文件"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401

        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '未找到上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'}), 400

        if file and allowed_file(file.filename):
            # 安全的文件名
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{user_id}_{timestamp}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # 保存文件
            file.save(file_path)
            
            # 读取文件内容
            content = ""
            try:
                if filename.endswith('.txt') or filename.endswith('.md'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                elif filename.endswith('.docx'):
                    from docx import Document
                    doc = Document(file_path)
                    content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                else:
                    content = "文件内容解析中，请稍候..."
            except Exception as e:
                print(f"文件内容解析失败: {e}")
                content = "文件内容解析失败，但文件已成功上传"

            return jsonify({
                'success': True,
                'message': '文件上传成功',
                'data': {
                    'filename': filename,
                    'original_name': file.filename,
                    'file_size': os.path.getsize(file_path),
                    'content': content[:2000],  # 限制返回内容长度
                    'upload_time': datetime.now().isoformat()
                }
            })
        else:
            return jsonify({
                'success': False, 
                'message': '不支持的文件格式，请上传 txt, pdf, doc, docx, md 格式文件'
            }), 400

    except Exception as e:
        return jsonify({'success': False, 'message': f'文件上传失败: {str(e)}'}), 500

@proposal_bp.route('/analyze', methods=['POST'])
def analyze_proposal():
    """分析开题报告内容"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401

        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'success': False, 'message': '开题报告内容不能为空'}), 400

        # 使用豆包AI分析开题报告
        client = get_doubao_api_client()
        if not client:
            return jsonify({'success': False, 'message': 'AI服务暂时不可用'}), 503

        analysis_prompt = f"""
        请深度分析以下开题报告内容，并提供详细的分析结果：

        开题报告内容：
        {content}

        请从以下几个方面进行分析：
        1. 研究题目的创新性和可行性评估
        2. 研究背景和意义的完整性
        3. 文献综述的质量和深度
        4. 研究方法的科学性和适用性
        5. 预期成果的合理性
        6. 存在的问题和改进建议
        7. 建议的论文大纲结构
        8. 推荐的研究方向和关键词

        请以JSON格式返回分析结果：
        {{
            "title_analysis": {{
                "innovation": "创新性评分和分析",
                "feasibility": "可行性评分和分析"
            }},
            "background_analysis": {{
                "completeness": "背景完整性评分",
                "significance": "研究意义分析"
            }},
            "literature_review": {{
                "quality": "文献综述质量评分",
                "depth": "综述深度分析"
            }},
            "methodology": {{
                "scientific": "方法科学性评分",
                "applicability": "方法适用性分析"
            }},
            "expected_results": {{
                "reasonableness": "预期成果合理性评分",
                "analysis": "成果分析"
            }},
            "suggestions": ["改进建议1", "改进建议2", "改进建议3"],
            "recommended_outline": {{
                "sections": [
                    {{"title": "章节标题", "subsections": ["子章节1", "子章节2"]}},
                    {{"title": "章节标题", "subsections": ["子章节1", "子章节2"]}}
                ]
            }},
            "keywords": ["关键词1", "关键词2", "关键词3"],
            "research_directions": ["研究方向1", "研究方向2"]
        }}
        """

        try:
            response = client.chat_completion([
                {"role": "user", "content": analysis_prompt}
            ])
            
            if response and 'content' in response:
                content_text = response['content']
                
                # 尝试解析JSON响应
                import re
                json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
                if json_match:
                    analysis_result = json.loads(json_match.group())
                    
                    return jsonify({
                        'success': True,
                        'data': analysis_result,
                        'message': '开题报告分析完成'
                    })
                else:
                    # 如果无法解析JSON，返回文本分析
                    return jsonify({
                        'success': True,
                        'data': {
                            'analysis_text': content_text,
                            'suggestions': ['请根据分析结果进行相应改进'],
                            'keywords': ['人工智能', '数据分析', '研究方法']
                        },
                        'message': '开题报告分析完成（文本格式）'
                    })
                    
        except Exception as api_error:
            print(f"AI分析失败: {api_error}")
            # 返回基础分析结果
            basic_analysis = {
                "title_analysis": {
                    "innovation": "中等 - 建议进一步突出创新点",
                    "feasibility": "较高 - 研究方法可行"
                },
                "background_analysis": {
                    "completeness": "良好 - 背景描述较为完整",
                    "significance": "明确 - 研究意义表述清晰"
                },
                "literature_review": {
                    "quality": "中等 - 需要补充更多相关文献",
                    "depth": "一般 - 建议深入分析关键理论"
                },
                "methodology": {
                    "scientific": "较好 - 研究方法基本科学",
                    "applicability": "适用 - 方法与研究目标匹配"
                },
                "expected_results": {
                    "reasonableness": "合理 - 预期成果设定适当",
                    "analysis": "预期成果描述清晰，具有可实现性"
                },
                "suggestions": [
                    "建议补充更多近期相关文献",
                    "可以进一步细化研究方法",
                    "建议明确研究的创新点和贡献",
                    "可以添加研究局限性讨论"
                ],
                "recommended_outline": {
                    "sections": [
                        {"title": "1. 绪论", "subsections": ["1.1 研究背景", "1.2 研究意义", "1.3 研究目标"]},
                        {"title": "2. 文献综述", "subsections": ["2.1 理论基础", "2.2 研究现状", "2.3 发展趋势"]},
                        {"title": "3. 研究方法", "subsections": ["3.1 研究设计", "3.2 数据收集", "3.3 分析方法"]},
                        {"title": "4. 预期成果", "subsections": ["4.1 理论贡献", "4.2 实践价值", "4.3 应用前景"]},
                        {"title": "5. 研究计划", "subsections": ["5.1 时间安排", "5.2 研究进度", "5.3 风险分析"]}
                    ]
                },
                "keywords": ["研究方法", "理论分析", "实证研究", "数据分析"],
                "research_directions": ["理论研究", "实证分析", "应用研究"]
            }
            
            return jsonify({
                'success': True,
                'data': basic_analysis,
                'message': '开题报告分析完成（基础分析）'
            })

    except Exception as e:
        return jsonify({'success': False, 'message': f'分析开题报告失败: {str(e)}'}), 500

@proposal_bp.route('/extract-info', methods=['POST'])
def extract_proposal_info():
    """从开题报告中提取论文基本信息"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401

        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'success': False, 'message': '开题报告内容不能为空'}), 400

        # 使用AI提取关键信息
        client = get_doubao_api_client()
        if client:
            extract_prompt = f"""
            请从以下开题报告中提取论文的基本信息：

            开题报告内容：
            {content}

            请提取以下信息并以JSON格式返回：
            {{
                "title": "论文标题",
                "field": "研究领域",
                "keywords": "关键词1,关键词2,关键词3",
                "description": "研究内容简述",
                "education_level": "学历层次(本科/硕士/博士)",
                "word_count": "预期字数"
            }}
            """
            
            try:
                response = client.chat_completion([
                    {"role": "user", "content": extract_prompt}
                ])
                
                if response and 'content' in response:
                    content_text = response['content']
                    import re
                    json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
                    if json_match:
                        extracted_info = json.loads(json_match.group())
                        return jsonify({
                            'success': True,
                            'data': extracted_info,
                            'message': '信息提取成功'
                        })
            except Exception as e:
                print(f"AI信息提取失败: {e}")

        # 简单的关键词提取（fallback）
        lines = content.split('\n')
        title = ""
        field = ""
        
        for line in lines:
            line = line.strip()
            if ('题目' in line or '标题' in line) and len(line) < 100:
                title = line.replace('题目:', '').replace('标题:', '').strip()
            elif ('领域' in line or '专业' in line) and len(line) < 50:
                field = line.replace('领域:', '').replace('专业:', '').strip()
        
        return jsonify({
            'success': True,
            'data': {
                'title': title or '基于开题报告的研究',
                'field': field or '计算机科学',
                'keywords': '研究方法,数据分析,理论研究',
                'description': '基于开题报告的深入研究',
                'education_level': '本科',
                'word_count': '8000'
            },
            'message': '信息提取成功（基础提取）'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'提取信息失败: {str(e)}'}), 500