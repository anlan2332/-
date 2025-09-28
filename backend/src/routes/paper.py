from flask import Blueprint, request, jsonify
import openai
import os
from dotenv import load_dotenv
import json
import time

# 加载环境变量
load_dotenv()

paper_bp = Blueprint('paper', __name__)

# 配置OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

@paper_bp.route('/generate-title', methods=['POST'])
def generate_title():
    """智能选题 - 根据关键词生成论文标题"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', '')
        education = data.get('education', '本科')
        field = data.get('field', '计算机科学')
        
        prompt = f"""
        请为{education}学历的学生生成5个{field}领域的论文标题，关键词：{keywords}
        
        要求：
        1. 标题要具体明确，避免过于宽泛
        2. 符合{education}学历的研究深度
        3. 具有一定的创新性和可行性
        4. 字数控制在15-25字之间
        
        请以JSON格式返回，格式如下：
        {{"titles": ["标题1", "标题2", "标题3", "标题4", "标题5"]}}
        """
        
        # 模拟AI响应（实际项目中替换为真实的OpenAI API调用）
        titles = [
            f"基于{keywords}的{field}系统设计与实现",
            f"{keywords}在{field}中的应用研究",
            f"面向{keywords}的智能{field}平台开发",
            f"{keywords}技术在{field}领域的优化策略",
            f"基于{keywords}的{field}创新方法研究"
        ]
        
        return jsonify({
            'success': True,
            'titles': titles,
            'message': '标题生成成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生成标题失败: {str(e)}'
        }), 500

@paper_bp.route('/generate-outline', methods=['POST'])
def generate_outline():
    """生成论文大纲"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        education = data.get('education', '本科')
        word_count = data.get('word_count', '8000')
        description = data.get('description', '')
        
        # 模拟大纲生成
        outline = {
            'title': title,
            'chapters': [
                {
                    'id': 1,
                    'title': '1. 引言',
                    'subsections': [
                        '1.1 研究背景',
                        '1.2 研究意义',
                        '1.3 研究目标',
                        '1.4 论文结构'
                    ],
                    'word_count': int(int(word_count) * 0.1)
                },
                {
                    'id': 2,
                    'title': '2. 文献综述',
                    'subsections': [
                        '2.1 国外研究现状',
                        '2.2 国内研究现状',
                        '2.3 研究不足与发展趋势'
                    ],
                    'word_count': int(int(word_count) * 0.2)
                },
                {
                    'id': 3,
                    'title': '3. 研究方法',
                    'subsections': [
                        '3.1 研究设计',
                        '3.2 数据收集',
                        '3.3 分析方法'
                    ],
                    'word_count': int(int(word_count) * 0.15)
                },
                {
                    'id': 4,
                    'title': '4. 结果与分析',
                    'subsections': [
                        '4.1 数据分析结果',
                        '4.2 结果讨论',
                        '4.3 发现与启示'
                    ],
                    'word_count': int(int(word_count) * 0.4)
                },
                {
                    'id': 5,
                    'title': '5. 结论',
                    'subsections': [
                        '5.1 研究总结',
                        '5.2 研究贡献',
                        '5.3 局限性与未来研究方向'
                    ],
                    'word_count': int(int(word_count) * 0.15)
                }
            ],
            'total_word_count': int(word_count),
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify({
            'success': True,
            'outline': outline,
            'message': '大纲生成成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生成大纲失败: {str(e)}'
        }), 500

@paper_bp.route('/generate-content', methods=['POST'])
def generate_content():
    """生成论文内容"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        chapter = data.get('chapter', '')
        subsection = data.get('subsection', '')
        word_count = data.get('word_count', 500)
        context = data.get('context', '')
        
        prompt = f"""
        请为论文《{title}》的{chapter} - {subsection}部分撰写内容。
        
        要求：
        1. 字数约{word_count}字
        2. 语言学术但自然，避免过于模式化
        3. 适当使用具体例子和数据
        4. 保持逻辑清晰，结构合理
        
        上下文信息：{context}
        """
        
        # 模拟内容生成
        content = f"""
        {subsection}是{chapter}的重要组成部分。在当前的研究背景下，{title}的相关研究显示出重要的学术价值和实践意义。

        根据现有文献分析，该领域的研究主要集中在以下几个方面：首先，理论基础的构建为后续研究提供了坚实的支撑；其次，方法论的创新推动了研究的深入发展；最后，实证研究的开展验证了理论的有效性。

        通过深入分析，我们发现当前研究存在一些不足之处。例如，在研究方法上还有待进一步完善，在数据收集和分析方面也需要更加严谨的处理。这些问题的存在为我们的研究提供了新的思路和方向。

        综合考虑各种因素，本研究将在现有基础上进行创新和发展，力求在理论和实践两个层面都有所突破。通过系统的研究设计和严格的实施过程，我们期望能够为该领域的发展做出有益的贡献。
        """
        
        return jsonify({
            'success': True,
            'content': content.strip(),
            'word_count': len(content.strip()),
            'message': '内容生成成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生成内容失败: {str(e)}'
        }), 500

@paper_bp.route('/polish-content', methods=['POST'])
def polish_content():
    """润色修改内容"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        style = data.get('style', 'academic')  # academic, natural, simple
        
        # 模拟润色处理
        polished_content = content.replace('。', '。\n').replace('，', '，')
        
        return jsonify({
            'success': True,
            'original_content': content,
            'polished_content': polished_content,
            'message': '内容润色成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'润色失败: {str(e)}'
        }), 500

@paper_bp.route('/reduce-ai-detection', methods=['POST'])
def reduce_ai_detection():
    """AIGC降重"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        # 模拟降重处理
        reduced_content = content.replace('研究', '探讨').replace('分析', '剖析').replace('发现', '观察到')
        
        return jsonify({
            'success': True,
            'original_content': content,
            'reduced_content': reduced_content,
            'ai_detection_rate': '15%',  # 模拟检测率
            'message': 'AI降重成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'降重失败: {str(e)}'
        }), 500

@paper_bp.route('/format-paper', methods=['POST'])
def format_paper():
    """格式调整"""
    try:
        data = request.get_json()
        content = data.get('content', '')
        format_type = data.get('format_type', 'standard')  # standard, apa, mla
        
        # 模拟格式调整
        formatted_content = f"# 论文标题\n\n{content}\n\n## 参考文献\n[1] 示例参考文献"
        
        return jsonify({
            'success': True,
            'formatted_content': formatted_content,
            'format_type': format_type,
            'message': '格式调整成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'格式调整失败: {str(e)}'
        }), 500

