import { useState, useEffect, useRef } from 'react'
import { MessageCircle, Minimize2, Send, X } from 'lucide-react'

const API_BASE_URL = 'https://5001-i362990uh7vzwuu0d0o9j-6532622b.e2b.dev'

export function ChatWindow() {
  const [isMinimized, setIsMinimized] = useState(true)
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(scrollToBottom, [messages])

  useEffect(() => {
    // 加载对话历史
    loadConversation()
  }, [])

  const loadConversation = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/get-conversation?conversation_id=default`)
      const data = await response.json()
      if (data.success) {
        setMessages(data.messages.map(msg => ({
          id: msg.id,
          type: msg.type,
          content: msg.content,
          timestamp: msg.timestamp
        })))
      }
    } catch (error) {
      console.error('加载对话历史失败:', error)
      // 设置欢迎消息
      setMessages([{
        id: 'welcome',
        type: 'ai',
        content: '您好！我是您的AI写作助手，可以帮助您进行论文写作。请告诉我您需要什么帮助？',
        timestamp: new Date().toLocaleString()
      }])
    }
  }

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date().toLocaleString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/send-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          conversation_id: 'default'
        })
      })

      const data = await response.json()
      
      if (data.success) {
        const aiMessage = {
          id: data.message_id,
          type: 'ai',
          content: data.response,
          timestamp: data.timestamp
        }
        setMessages(prev => [...prev, aiMessage])
      } else {
        throw new Error(data.message)
      }
    } catch (error) {
      console.error('发送消息失败:', error)
      const errorMessage = {
        id: Date.now().toString(),
        type: 'ai',
        content: '抱歉，我现在无法回复您的消息。请稍后再试。',
        timestamp: new Date().toLocaleString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearConversation = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/chat/clear-conversation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: 'default'
        })
      })
      setMessages([{
        id: 'welcome',
        type: 'ai',
        content: '对话已清空。我是您的AI写作助手，有什么可以帮助您的吗？',
        timestamp: new Date().toLocaleString()
      }])
    } catch (error) {
      console.error('清空对话失败:', error)
    }
  }

  if (isMinimized) {
    return (
      <div
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: '60px',
          height: '60px',
          backgroundColor: '#3b82f6',
          borderRadius: '50%',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          zIndex: 1000
        }}
        onClick={() => setIsMinimized(false)}
      >
        <MessageCircle size={24} color="white" />
      </div>
    )
  }

  return (
    <div className="chat-window">
      {/* 聊天头部 */}
      <div className="chat-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>AI写作助手</span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={clearConversation}
              style={{ 
                background: 'none', 
                border: 'none', 
                color: 'white', 
                cursor: 'pointer',
                fontSize: '12px',
                padding: '4px 8px',
                borderRadius: '4px'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.1)'}
              onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
            >
              清空
            </button>
            <button
              onClick={() => setIsMinimized(true)}
              style={{ 
                background: 'none', 
                border: 'none', 
                color: 'white', 
                cursor: 'pointer',
                padding: '4px',
                borderRadius: '4px'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.1)'}
              onMouseOut={(e) => e.target.style.backgroundColor = 'transparent'}
            >
              <Minimize2 size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* 消息列表 */}
      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-content">
              {message.content}
            </div>
            <div style={{ 
              fontSize: '10px', 
              color: '#9ca3af', 
              marginTop: '4px',
              textAlign: message.type === 'user' ? 'right' : 'left'
            }}>
              {message.timestamp}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message ai">
            <div className="message-content">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div className="loading" />
                正在思考...
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="chat-input-area">
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            className="chat-input"
            placeholder="输入您的问题..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!inputValue.trim() || isLoading}
            style={{
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              padding: '8px',
              cursor: inputValue.trim() && !isLoading ? 'pointer' : 'not-allowed',
              opacity: inputValue.trim() && !isLoading ? 1 : 0.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <Send size={16} />
          </button>
        </div>
        <div style={{ 
          fontSize: '10px', 
          color: '#9ca3af', 
          marginTop: '4px',
          textAlign: 'center'
        }}>
          按 Enter 发送，Shift + Enter 换行
        </div>
      </div>
    </div>
  )
}