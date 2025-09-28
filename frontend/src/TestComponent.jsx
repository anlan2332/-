import { useState } from 'react'

export function TestComponent() {
  const [message, setMessage] = useState('测试组件正常工作!')

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h2>测试页面</h2>
      <p>{message}</p>
      <button 
        onClick={() => setMessage('按钮点击成功!')}
        style={{
          padding: '10px 20px',
          backgroundColor: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        点击测试
      </button>
    </div>
  )
}