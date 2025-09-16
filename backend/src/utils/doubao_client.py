"""
豆包API客户端
火山引擎豆包大模型API集成
"""
import os
import json
import requests
from typing import Dict, List, Optional, Any

class DoubaoClient:
    """豆包API客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://ark.cn-beijing.volces.com/api/v3"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def chat_completions(self, 
                        model: str = "doubao-seed-1-6-250615",
                        messages: List[Dict[str, Any]] = None,
                        temperature: float = 0.7,
                        max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        发送聊天完成请求
        
        Args:
            model: 模型名称，默认为 doubao-seed-1-6-250615
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大tokens数
            
        Returns:
            API响应结果
        """
        if messages is None:
            messages = []
            
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"豆包API请求失败: {e}")
            return {
                "error": {
                    "message": f"API请求失败: {str(e)}",
                    "type": "api_error"
                }
            }
    
    def generate_thesis_content(self, 
                               title: str, 
                               field: str, 
                               education_level: str, 
                               keywords: str, 
                               description: str = "",
                               assistant_instructions: str = "") -> Dict[str, Any]:
        """
        生成论文内容
        
        Args:
            title: 论文标题
            field: 研究领域
            education_level: 教育层次
            keywords: 关键词
            description: 补充说明
            assistant_instructions: 助手指令
            
        Returns:
            生成结果
        """
        
        # 构建系统提示词
        system_prompt = f"""你是一个专业的学术论文写作助手。请根据以下要求生成高质量的学术论文内容。

{assistant_instructions}

论文要求：
- 标题：{title}
- 研究领域：{field}
- 教育层次：{education_level}
- 关键词：{keywords}
- 补充说明：{description}

请生成符合学术规范的论文内容，包括：
1. 摘要
2. 引言/绪论
3. 文献综述
4. 研究方法
5. 结论
6. 参考文献

要求：
- 内容严谨、逻辑清晰
- 符合{education_level}水平要求
- 语言学术化，避免口语化表达
- 适当引用相关文献
- 结构完整，层次分明
"""
        
        user_prompt = f"请为题目「{title}」撰写一篇{education_level}水平的学术论文，研究领域为{field}。"
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user", 
                "content": user_prompt
            }
        ]
        
        return self.chat_completions(
            messages=messages,
            temperature=0.7,
            max_tokens=4000
        )
    
    def generate_outline(self, title: str, field: str, education_level: str) -> Dict[str, Any]:
        """
        生成论文大纲
        
        Args:
            title: 论文标题
            field: 研究领域  
            education_level: 教育层次
            
        Returns:
            大纲生成结果
        """
        
        system_prompt = f"""你是一个专业的学术论文大纲生成助手。请为给定的论文题目生成详细的论文大纲。

要求：
1. 大纲结构要完整，包括各个主要章节
2. 每个章节要有明确的研究内容和目标
3. 符合{education_level}水平的学术要求
4. 逻辑层次清晰，前后呼应
5. 适合{field}领域的研究特点

大纲格式：
- 使用数字编号（1. 1.1 1.1.1）
- 每个章节标题简洁明确
- 包含主要研究内容说明
"""
        
        user_prompt = f"请为论文题目「{title}」生成详细的论文大纲，研究领域为{field}，教育层次为{education_level}。"
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
        
        return self.chat_completions(
            messages=messages,
            temperature=0.6,
            max_tokens=2000
        )
    
    def generate_references(self, title: str, field: str, count: int = 15) -> Dict[str, Any]:
        """
        生成参考文献
        
        Args:
            title: 论文标题
            field: 研究领域
            count: 文献数量
            
        Returns:
            参考文献生成结果
        """
        
        system_prompt = f"""你是一个专业的学术文献检索助手。请为给定的论文题目生成相关的参考文献。

要求：
1. 生成{count}篇相关文献
2. 包括国内外权威期刊文献
3. 文献要真实可信，符合学术规范
4. 涵盖{field}领域的重要研究
5. 文献格式符合GB/T 7714-2015标准
6. 包括近5年的新研究成果

文献格式示例：
[1] 作者. 题名[J]. 刊名, 年, 卷(期): 起止页码.
[2] 作者. 题名[M]. 出版地: 出版者, 出版年.
"""
        
        user_prompt = f"请为论文题目「{title}」生成{count}篇{field}领域的相关参考文献，按照GB/T 7714-2015标准格式。"
        
        messages = [
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
        
        return self.chat_completions(
            messages=messages,
            temperature=0.5,
            max_tokens=2000
        )


def get_doubao_client(api_key: str = None) -> DoubaoClient:
    """
    获取豆包客户端实例
    
    Args:
        api_key: API密钥，如果为None则使用默认密钥
        
    Returns:
        DoubaoClient实例
    """
    if api_key is None:
        api_key = "039c31ba-ebd5-429b-8e88-593eb0e0dc67"  # 用户提供的API密钥
    
    return DoubaoClient(api_key)