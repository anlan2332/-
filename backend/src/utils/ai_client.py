import os
import requests
import json
from datetime import datetime

class AIClient:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.base_url = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        
    def chat_completion(self, messages, model="gpt-3.5-turbo", temperature=0.7, max_tokens=2000):
        """调用AI聊天接口"""
        try:
            # 模拟AI响应，因为这是演示版本
            user_message = messages[-1]['content'] if messages else ""
            
            # 根据消息内容生成相应回复
            if "论文" in user_message or "标题" in user_message:
                response_content = f"根据您的要求，我为您生成了关于「{user_message}」的论文建议。这是一个很有研究价值的主题。"
            elif "大纲" in user_message:
                response_content = """我为您生成了论文大纲：
1. 引言
   1.1 研究背景
   1.2 研究意义
   1.3 研究目标
2. 文献综述
   2.1 国内研究现状
   2.2 国外研究现状
   2.3 研究空白
3. 研究方法
   3.1 研究设计
   3.2 数据收集
   3.3 分析方法
4. 结果与分析
5. 结论与建议"""
            elif "文献" in user_message or "参考" in user_message:
                response_content = "我为您找到了相关的学术文献资源，包括最新的研究成果和权威期刊文章。"
            else:
                response_content = f"感谢您的提问。我理解您想了解「{user_message}」相关内容，我会为您提供专业的学术写作指导。"
            
            return {
                'success': True,
                'data': {
                    'content': response_content,
                    'model': model,
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_text(self, prompt, model="gpt-3.5-turbo", temperature=0.7, max_tokens=1000):
        """生成文本"""
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(messages, model, temperature, max_tokens)

# 全局AI客户端实例
ai_client = AIClient()