from flask import Blueprint, request, jsonify
import openai
import os
from dotenv import load_dotenv
import json
import time

# 加载环境变量
load_dotenv()

chat_bp = Blueprint('chat', __name__)

# 配置OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

@chat_bp.route('/send-message', methods=['POST'])
def send_message():
    """发送聊天消息"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', 'default')
        context = data.get('context', {})
        
        # 模拟AI回复逻辑
        response_message = generate_ai_response(message, context)
        
        # 保存对话记录（实际项目中应该保存到数据库）
        conversation_record = {
            'id': f'msg_{int(time.time())}',
            'conversation_id': conversation_id,
            'user_message': message,
            'ai_response': response_message,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'context': context
        }
        
        return jsonify({
            'success': True,
            'response': response_message,
            'conversation_id': conversation_id,
            'message_id': conversation_record['id'],
            'timestamp': conversation_record['timestamp']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发送消息失败: {str(e)}'
        }), 500

def generate_ai_response(user_message, context):
    """生成AI回复"""
    message_lower = user_message.lower()
    
    # 论文选题相关
    if any(keyword in message_lower for keyword in ['选题', '题目', '主题']):
        return """关于论文选题，我建议您从以下几个方面考虑：

1. **选择熟悉的领域**：选择您有一定基础和兴趣的研究领域
2. **确保资料充足**：确保有足够的研究资料和文献支撑
3. **题目要具体**：避免过于宽泛，要有明确的研究范围
4. **具有创新性**：在现有研究基础上有所创新和突破
5. **符合学历要求**：题目难度要与您的学历层次相匹配

您可以告诉我您的专业领域和感兴趣的方向，我来为您推荐具体的题目。"""

    # 大纲相关
    elif any(keyword in message_lower for keyword in ['大纲', '结构', '框架']):
        return """论文大纲是论文写作的重要基础，一般包括以下结构：

**标准论文结构：**
1. **引言部分**（10-15%）
   - 研究背景
   - 研究意义
   - 研究目标
   - 论文结构

2. **文献综述**（20-25%）
   - 国内外研究现状
   - 理论基础
   - 研究不足

3. **研究方法**（15-20%）
   - 研究设计
   - 数据收集
   - 分析方法

4. **结果与分析**（35-40%）
   - 实证分析
   - 结果讨论
   - 发现与启示

5. **结论**（10-15%）
   - 研究总结
   - 贡献与局限
   - 未来研究方向

我可以根据您的具体题目帮您制定详细的大纲。"""

    # 写作技巧相关
    elif any(keyword in message_lower for keyword in ['写作', '技巧', '方法']):
        return """论文写作的关键技巧包括：

**语言表达：**
- 使用学术语言，但保持自然流畅
- 避免过于复杂的句式，确保逻辑清晰
- 适当使用专业术语，但要解释清楚

**结构安排：**
- 每个段落都要有明确的主题
- 段落之间要有逻辑连接
- 使用过渡词语增强连贯性

**内容充实：**
- 多使用具体的例子和数据
- 引用权威文献支撑观点
- 保持客观中立的学术态度

**格式规范：**
- 严格按照学校要求的格式
- 注意引用格式的统一性
- 图表要清晰且有说明

需要我针对某个具体方面详细指导吗？"""

    # 格式相关
    elif any(keyword in message_lower for keyword in ['格式', '引用', '参考文献']):
        return """论文格式要求通常包括：

**基本格式：**
- 字体：宋体或Times New Roman
- 字号：正文小四号，标题适当加大
- 行距：1.5倍或2倍行距
- 页边距：上下2.5cm，左右2cm

**引用格式：**
- 国标GB/T 7714格式（推荐）
- APA格式（心理学、教育学常用）
- MLA格式（文学、语言学常用）

**参考文献：**
- 期刊：作者.题名[J].期刊名,年份,卷(期):页码.
- 图书：作者.书名[M].出版地:出版社,年份:页码.
- 网络资源：作者.题名[EB/OL].网址,访问日期.

**注意事项：**
- 引用要准确，避免断章取义
- 参考文献要新颖，近5年的文献占70%以上
- 中英文文献比例要合理

需要我帮您检查具体的格式问题吗？"""

    # 降重相关
    elif any(keyword in message_lower for keyword in ['降重', '查重', '重复率']):
        return """关于论文降重，我可以提供以下建议：

**降重策略：**
1. **同义词替换**：用近义词替换重复的词汇
2. **句式变换**：改变句子结构，主动语态变被动语态
3. **表述调整**：用自己的话重新组织语言
4. **增加原创内容**：加入自己的分析和见解

**注意事项：**
- 不要过度降重，保持学术性
- 确保修改后语义不变
- 保持逻辑的连贯性
- 重要的专业术语不要随意更改

**检测工具：**
- 知网查重（学校官方）
- 维普查重
- 万方查重
- PaperPass等

一般要求重复率在10-15%以下，具体标准以学校要求为准。

需要我帮您分析具体的重复内容吗？"""

    # 默认回复
    else:
        return f"""我理解您的问题："{user_message}"

作为您的AI写作助手，我可以在以下方面为您提供帮助：

📝 **论文写作指导**
- 选题建议和题目优化
- 大纲结构设计
- 内容撰写指导
- 语言表达改进

📚 **文献研究支持**
- 文献检索技巧
- 参考文献整理
- 研究现状分析
- 理论框架构建

🔧 **技术问题解决**
- 格式调整指导
- 查重降重建议
- 图表制作帮助
- 数据分析方法

请告诉我您具体需要什么帮助，我会为您提供更详细的指导。您也可以直接描述您遇到的问题，我来为您分析解决方案。"""

@chat_bp.route('/get-conversation', methods=['GET'])
def get_conversation():
    """获取对话历史"""
    try:
        conversation_id = request.args.get('conversation_id', 'default')
        
        # 模拟对话历史（实际项目中从数据库获取）
        conversation_history = [
            {
                'id': 'msg_1',
                'type': 'ai',
                'content': '您好！我是您的AI写作助手，可以帮助您进行论文写作。请告诉我您需要什么帮助？',
                'timestamp': '2024-01-01 10:00:00'
            }
        ]
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'messages': conversation_history,
            'total_count': len(conversation_history)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取对话历史失败: {str(e)}'
        }), 500

@chat_bp.route('/clear-conversation', methods=['POST'])
def clear_conversation():
    """清空对话历史"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id', 'default')
        
        # 实际项目中应该从数据库删除对话记录
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'message': '对话历史已清空'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'清空对话失败: {str(e)}'
        }), 500

