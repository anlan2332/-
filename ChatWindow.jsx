import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card } from '@/components/ui/card.jsx'
import { MessageCircle, Settings, Send, Minimize2, Maximize2, Loader2 } from 'lucide-react'
import apiService from '../services/api.js'

export function ChatWindow() {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isMinimized, setIsMinimized] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  // 初始化聊天
  useEffect(() => {
    loadConversation()
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadConversation = async () => {
    try {
      const response = await apiService.getConversation()
      if (response.success) {
        setMessages(response.messages.map(msg => ({
          id: msg.id,
          type: msg.type,
          content: msg.content,
          timestamp: msg.timestamp
        })))
      }
    } catch (error) {
      console.error('加载对话历史失败:', error)
      // 设置默认欢迎消息
      setMessages([{
        id: 'welcome',
        type: 'ai',
        content: '您好！我是您的AI写作助手，可以帮助您：',
        features: [
          '论文选题建议',
          '大纲结构优化', 
          '内容撰写指导',
          '格式规范检查',
          '文献检索支持',
          'AI降重优化'
        ]
      }])
    }
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toLocaleTimeString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await apiService.sendMessage({
        message: userMessage.content,
        conversation_id: 'default',
        context: {}
      })

      if (response.success) {
        const aiMessage = {
          id: response.message_id,
          type: 'ai',
          content: response.response,
          timestamp: response.timestamp
        }
        setMessages(prev => [...prev, aiMessage])
      } else {
        throw new Error(response.message)
      }
    } catch (error) {
      console.error('发送消息失败:', error)
      const errorMessage = {
        id: Date.now().toString(),
        type: 'ai',
        content: '抱歉，我暂时无法回复您的消息。请检查网络连接或稍后再试。如果问题持续，请确保后端服务正在运行。',
        timestamp: new Date().toLocaleTimeString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const clearConversation = async () => {
    try {
      await apiService.clearConversation({ conversation_id: 'default' })
      setMessages([{
        id: 'welcome',
        type: 'ai',
        content: '对话已清空。我是您的AI写作助手，请告诉我您需要什么帮助？',
        features: [
          '论文选题建议',
          '大纲结构优化', 
          '内容撰写指导',
          '格式规范检查',
          '文献检索支持',
          'AI降重优化'
        ]
      }])
    } catch (error) {
      console.error('清空对话失败:', error)
    }
  }

  if (isMinimized) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <Button
          onClick={() => setIsMinimized(false)}
          className="rounded-full w-12 h-12 bg-blue-600 hover:bg-blue-700 shadow-lg"
        >
          <MessageCircle className="h-6 w-6" />
        </Button>
      </div>
    )
  }

  return (
    <Card className="fixed bottom-6 right-6 w-80 bg-white shadow-lg border z-50">
      {/* 聊天窗口头部 */}
      <div className="flex items-center justify-between p-3 border-b bg-blue-50">
        <div className="flex items-center space-x-2">
          <MessageCircle className="h-4 w-4 text-blue-600" />
          <span className="font-medium text-sm text-blue-800">智能清言：ChatGLM & AutoGLM</span>
        </div>
        <div className="flex space-x-1">
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => setIsMinimized(true)}
          >
            <Minimize2 className="h-4 w-4" />
          </Button>
          <Button 
            variant="ghost" 
            size="sm"
            onClick={clearConversation}
            title="清空对话"
          >
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      {/* 消息区域 */}
      <div className="p-4 h-64 overflow-y-auto bg-gray-50">
        <div className="space-y-3">
          {messages.map((message) => (
            <div key={message.id} className={`${
              message.type === 'ai' ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-200'
            } p-3 rounded-lg border`}>
              <div className="text-sm whitespace-pre-wrap">{message.content}</div>
              {message.features && (
                <ul className="text-xs mt-2 space-y-1 text-gray-600">
                  {message.features.map((feature, index) => (
                    <li key={index}>• {feature}</li>
                  ))}
                </ul>
              )}
              {message.timestamp && (
                <div className="text-xs text-gray-500 mt-2">
                  {message.timestamp}
                </div>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className="bg-blue-50 border-blue-200 p-3 rounded-lg border">
              <div className="flex items-center space-x-2 text-sm">
                <Loader2 className="h-3 w-3 animate-spin" />
                <span>AI正在思考...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      {/* 输入区域 */}
      <div className="p-3 border-t bg-white">
        <div className="flex space-x-2">
          <Input 
            placeholder="欢迎来到清言，您可以问我任何问题" 
            className="flex-1 text-sm"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
          />
          <Button 
            size="sm" 
            className="bg-blue-600 hover:bg-blue-700"
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        <div className="text-xs text-gray-500 mt-2">
          按Enter发送，Shift+Enter换行
        </div>
      </div>
    </Card>
  )
}

