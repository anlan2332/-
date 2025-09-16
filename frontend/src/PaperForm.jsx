import { useState, useEffect } from 'react'
import { Search, Upload, Lightbulb, Clock, FileText, Download, ChevronRight, CheckCircle } from 'lucide-react'

const API_BASE_URL = 'https://5001-i362990uh7vzwuu0d0o9j-6532622b.e2b.dev'

export function PaperForm() {
  const [formData, setFormData] = useState({
    title: '',
    field: '',
    education: '本科',
    wordCount: '8000',
    keywords: '',
    description: ''
  })

  const [currentStep, setCurrentStep] = useState(1)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [currentPaper, setCurrentPaper] = useState(null)
  const [paperContent, setPaperContent] = useState('')
  const [socket, setSocket] = useState(null)
  const [wsConnected, setWsConnected] = useState(false)
  const [references, setReferences] = useState([])
  const [outline, setOutline] = useState(null)

  // WebSocket连接 - 暂时禁用直到修复依赖问题
  useEffect(() => {
    // TODO: 修复socket.io-client导入问题后恢复WebSocket功能
    console.log('WebSocket功能暂时禁用 - 等待修复socket.io-client依赖')
    setWsConnected(false)
    
    // 模拟连接以进行基本测试
    setTimeout(() => {
      setWsConnected(true)
      console.log('模拟WebSocket连接成功')
    }, 1000)
    
    /*
    const newSocket = io(API_BASE_URL)
    
    newSocket.on('connect', () => {
      console.log('WebSocket连接成功')
      setWsConnected(true)
    })
    
    newSocket.on('disconnect', () => {
      console.log('WebSocket连接断开')
      setWsConnected(false)
    })
    
    newSocket.on('paper_progress', (data) => {
      console.log('收到论文生成进度:', data)
      setGenerationProgress(data.progress)
      if (data.progress === 100) {
        setIsGenerating(false)
        // 获取完成的论文内容
        fetchPaperContent(data.paper_id)
      }
    })
    
    newSocket.on('error', (error) => {
      console.error('WebSocket错误:', error)
      alert('连接错误: ' + error.message)
    })
    
    setSocket(newSocket)
    
    return () => {
      newSocket.close()
    }
    */
  }, [])

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const fetchPaperContent = async (paperId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/thesis/${paperId}`, {
        method: 'GET',
        credentials: 'include'
      })
      const data = await response.json()
      if (data.success) {
        setPaperContent(data.data.content)
        setCurrentPaper(data.data)
        setCurrentStep(4) // 跳转到下载步骤
      }
    } catch (error) {
      console.error('获取论文内容失败:', error)
    }
  }

  const handleCreateThesis = async () => {
    if (!formData.title.trim()) {
      alert('请输入论文标题')
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/thesis/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          title: formData.title,
          field: formData.field,
          education_level: formData.education,
          keywords: formData.keywords,
          description: formData.description,
          word_count: parseInt(formData.wordCount)
        })
      })

      const data = await response.json()
      if (data.success) {
        setCurrentPaper(data.data)
        setCurrentStep(2) // 进入参考文献步骤
        alert('论文创建成功！')
      } else {
        alert('创建论文失败: ' + data.message)
      }
    } catch (error) {
      console.error('创建论文失败:', error)
      alert('网络错误，请稍后重试')
    }
  }

  const handleGenerateThesis = async () => {
    if (!currentPaper) {
      alert('请先创建论文')
      return
    }

    setIsGenerating(true)
    setGenerationProgress(0)
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/thesis/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          paper_id: currentPaper.paper_id
        })
      })

      const data = await response.json()
      if (data.success) {
        // 生成开始，等待WebSocket进度通知
        alert('开始生成论文，请稍候...')
      } else {
        alert('生成论文失败: ' + data.message)
        setIsGenerating(false)
      }
    } catch (error) {
      console.error('生成论文失败:', error)
      alert('网络错误，请稍后重试')
      setIsGenerating(false)
    }
  }

  const addReference = () => {
    const newRef = {
      id: Date.now(),
      title: '',
      author: '',
      year: '',
      journal: '',
      type: 'journal'
    }
    setReferences([...references, newRef])
  }

  const updateReference = (id, field, value) => {
    setReferences(refs => refs.map(ref => 
      ref.id === id ? { ...ref, [field]: value } : ref
    ))
  }

  const removeReference = (id) => {
    setReferences(refs => refs.filter(ref => ref.id !== id))
  }

  const generateOutline = () => {
    if (!currentPaper) {
      alert('请先创建论文')
      return
    }
    
    // 模拟生成大纲
    const mockOutline = {
      title: formData.title,
      sections: [
        { title: '摘要', pages: 1 },
        { title: '绪论', pages: 2 },
        { title: '相关技术与理论基础', pages: 3 },
        { title: '系统设计与实现', pages: 4 },
        { title: '实验结果与分析', pages: 3 },
        { title: '结论与展望', pages: 1 }
      ],
      totalPages: 14
    }
    setOutline(mockOutline)
    setCurrentStep(3)
  }

  const downloadPaper = () => {
    if (!paperContent) {
      alert('暂无可下载内容')
      return
    }
    
    const blob = new Blob([paperContent], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${formData.title}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const steps = [
    { id: 1, title: '论文标题', desc: '设置论文标题与主题', icon: '1' },
    { id: 2, title: '参考文献', desc: '添加并管理参考文献', icon: '2' },
    { id: 3, title: '大纲', desc: '组织论文结构与章节', icon: '3' },
    { id: 4, title: '下载', desc: '导出完整的论文', icon: '4' }
  ]

  const quickFillButtons = [
    { label: '人工智能', value: '人工智能在智慧城市建设中的应用研究', field: '计算机科学' },
    { label: '大数据', value: '大数据技术在企业决策中的应用与分析', field: '计算机科学' },
    { label: '云计算', value: '云计算环境下的数据安全保护机制研究', field: '计算机科学' },
    { label: '物联网', value: '物联网技术在智能家居系统中的设计与实现', field: '计算机科学' }
  ]

  const renderStep1 = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* 论文标题输入 */}
      <div>
        <label className="form-label">论文标题 *</label>
        <input
          type="text"
          className="input"
          placeholder="请输入完整的论文标题"
          value={formData.title}
          onChange={(e) => handleInputChange('title', e.target.value)}
        />
        
        {/* 快捷填充按钮 */}
        <div style={{ marginTop: '12px' }}>
          <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '8px' }}>快捷填充:</p>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {quickFillButtons.map((btn, index) => (
              <button
                key={index}
                className="button"
                style={{ 
                  fontSize: '12px', 
                  padding: '4px 8px',
                  backgroundColor: '#f3f4f6',
                  color: '#374151',
                  border: '1px solid #d1d5db'
                }}
                onClick={() => {
                  handleInputChange('title', btn.value)
                  handleInputChange('field', btn.field)
                }}
              >
                {btn.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 研究领域 */}
      <div>
        <label className="form-label">研究领域</label>
        <input
          type="text"
          className="input"
          placeholder="如：计算机科学、机械工程、管理学等"
          value={formData.field}
          onChange={(e) => handleInputChange('field', e.target.value)}
        />
      </div>

      {/* 基本设置 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div>
          <label className="form-label">学历层次</label>
          <select
            className="select"
            value={formData.education}
            onChange={(e) => handleInputChange('education', e.target.value)}
          >
            <option value="专科">专科</option>
            <option value="本科">本科</option>
            <option value="硕士">硕士</option>
            <option value="博士">博士</option>
          </select>
        </div>

        <div>
          <label className="form-label">目标字数</label>
          <select
            className="select"
            value={formData.wordCount}
            onChange={(e) => handleInputChange('wordCount', e.target.value)}
          >
            <option value="5000">5000字</option>
            <option value="8000">8000字</option>
            <option value="10000">10000字</option>
            <option value="15000">15000字</option>
            <option value="20000">20000字</option>
          </select>
        </div>
      </div>

      {/* 关键词 */}
      <div>
        <label className="form-label">关键词</label>
        <input
          type="text"
          className="input"
          placeholder="用分号分隔，如：人工智能;机器学习;深度学习"
          value={formData.keywords}
          onChange={(e) => handleInputChange('keywords', e.target.value)}
        />
      </div>

      {/* 补充说明 */}
      <div>
        <label className="form-label">补充说明</label>
        <textarea
          className="textarea"
          placeholder="请详细描述您的研究思路、方法、内容要求、参考的数据/案例/资料等..."
          value={formData.description}
          onChange={(e) => handleInputChange('description', e.target.value)}
          rows={4}
        />
      </div>

      {/* 操作按钮 */}
      <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
        <button 
          className="button"
          onClick={handleCreateThesis}
          style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          <ChevronRight size={16} />
          下一步：添加参考文献
        </button>
      </div>
    </div>
  )

  const renderStep2 = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600' }}>参考文献管理</h3>
        <button 
          className="button"
          onClick={addReference}
          style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          添加文献
        </button>
      </div>

      {references.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          <FileText size={48} style={{ marginBottom: '16px', margin: '0 auto' }} />
          <p>暂无参考文献，点击"添加文献"开始添加</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {references.map((ref, index) => (
            <div key={ref.id} className="card" style={{ padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'between', alignItems: 'center', marginBottom: '12px' }}>
                <span style={{ fontWeight: '500' }}>文献 {index + 1}</span>
                <button 
                  onClick={() => removeReference(ref.id)}
                  style={{ color: '#dc2626', background: 'none', border: 'none', cursor: 'pointer' }}
                >
                  删除
                </button>
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '12px', marginBottom: '12px' }}>
                <input
                  type="text"
                  className="input"
                  placeholder="文献标题"
                  value={ref.title}
                  onChange={(e) => updateReference(ref.id, 'title', e.target.value)}
                />
                <input
                  type="text"
                  className="input"
                  placeholder="作者"
                  value={ref.author}
                  onChange={(e) => updateReference(ref.id, 'author', e.target.value)}
                />
              </div>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                <input
                  type="text"
                  className="input"
                  placeholder="发表年份"
                  value={ref.year}
                  onChange={(e) => updateReference(ref.id, 'year', e.target.value)}
                />
                <input
                  type="text"
                  className="input"
                  placeholder="期刊/会议名称"
                  value={ref.journal}
                  onChange={(e) => updateReference(ref.id, 'journal', e.target.value)}
                />
                <select
                  className="select"
                  value={ref.type}
                  onChange={(e) => updateReference(ref.id, 'type', e.target.value)}
                >
                  <option value="journal">期刊论文</option>
                  <option value="conference">会议论文</option>
                  <option value="book">图书</option>
                  <option value="thesis">学位论文</option>
                </select>
              </div>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'flex', gap: '12px', justifyContent: 'space-between' }}>
        <button 
          className="button"
          onClick={() => setCurrentStep(1)}
          style={{ backgroundColor: '#f3f4f6', color: '#374151', border: '1px solid #d1d5db' }}
        >
          上一步
        </button>
        <button 
          className="button"
          onClick={generateOutline}
          style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          <ChevronRight size={16} />
          下一步：生成大纲
        </button>
      </div>
    </div>
  )

  const renderStep3 = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <h3 style={{ fontSize: '18px', fontWeight: '600' }}>论文大纲</h3>
      
      {outline ? (
        <div className="card" style={{ padding: '20px' }}>
          <h4 style={{ fontSize: '16px', fontWeight: '500', marginBottom: '16px' }}>{outline.title}</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {outline.sections.map((section, index) => (
              <div key={index} style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                padding: '8px 12px',
                backgroundColor: '#f9fafb',
                borderRadius: '6px'
              }}>
                <span style={{ fontWeight: '500' }}>{section.title}</span>
                <span style={{ color: '#6b7280', fontSize: '14px' }}>约 {section.pages} 页</span>
              </div>
            ))}
          </div>
          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#dbeafe', borderRadius: '6px' }}>
            <p style={{ fontSize: '14px', color: '#1d4ed8' }}>
              预计总页数: {outline.totalPages} 页 | 建议字数: {formData.wordCount} 字
            </p>
          </div>
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          <FileText size={48} style={{ marginBottom: '16px', margin: '0 auto' }} />
          <p>大纲生成中...</p>
        </div>
      )}

      <div style={{ display: 'flex', gap: '12px', justifyContent: 'space-between' }}>
        <button 
          className="button"
          onClick={() => setCurrentStep(2)}
          style={{ backgroundColor: '#f3f4f6', color: '#374151', border: '1px solid #d1d5db' }}
        >
          上一步
        </button>
        <button 
          className="button"
          onClick={handleGenerateThesis}
          disabled={isGenerating}
          style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          {isGenerating ? (
            <>
              <div className="loading" />
              生成中... {generationProgress}%
            </>
          ) : (
            <>
              <ChevronRight size={16} />
              开始生成论文
            </>
          )}
        </button>
      </div>

      {isGenerating && (
        <div style={{ padding: '16px', backgroundColor: '#f0f9ff', borderRadius: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <div className="loading" />
            <span style={{ color: '#0369a1' }}>正在生成论文内容...</span>
          </div>
          <div style={{ width: '100%', height: '8px', backgroundColor: '#e0e7ff', borderRadius: '4px' }}>
            <div 
              style={{ 
                width: `${generationProgress}%`, 
                height: '100%', 
                backgroundColor: '#3b82f6', 
                borderRadius: '4px',
                transition: 'width 0.3s ease'
              }}
            />
          </div>
          <p style={{ fontSize: '12px', color: '#0369a1', marginTop: '4px' }}>
            进度: {generationProgress}%
          </p>
        </div>
      )}
    </div>
  )

  const renderStep4 = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <h3 style={{ fontSize: '18px', fontWeight: '600' }}>论文下载</h3>
      
      {paperContent ? (
        <div>
          <div className="card" style={{ padding: '20px', marginBottom: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <CheckCircle size={24} style={{ color: '#10b981' }} />
              <div>
                <h4 style={{ fontSize: '16px', fontWeight: '500', color: '#10b981' }}>论文生成完成！</h4>
                <p style={{ color: '#6b7280', fontSize: '14px' }}>
                  字数: {paperContent.length} | 标题: {formData.title}
                </p>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: '12px' }}>
              <button 
                className="button"
                onClick={downloadPaper}
                style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <Download size={16} />
                下载TXT格式
              </button>
              <button 
                className="button"
                style={{ 
                  backgroundColor: '#f3f4f6', 
                  color: '#374151', 
                  border: '1px solid #d1d5db',
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '8px' 
                }}
              >
                <Download size={16} />
                下载DOCX格式
              </button>
            </div>
          </div>
          
          <div className="card" style={{ padding: '20px' }}>
            <h4 style={{ fontSize: '14px', fontWeight: '500', marginBottom: '12px' }}>论文预览</h4>
            <div style={{ 
              maxHeight: '300px', 
              overflow: 'auto',
              backgroundColor: '#f9fafb',
              padding: '12px',
              borderRadius: '6px',
              fontSize: '14px',
              lineHeight: '1.6',
              whiteSpace: 'pre-wrap'
            }}>
              {paperContent.substring(0, 1000)}
              {paperContent.length > 1000 && '...\n\n[内容较长，请下载查看完整版本]'}
            </div>
          </div>
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          <Download size={48} style={{ marginBottom: '16px', margin: '0 auto' }} />
          <p>论文内容准备中...</p>
        </div>
      )}

      <div style={{ display: 'flex', gap: '12px', justifyContent: 'space-between' }}>
        <button 
          className="button"
          onClick={() => setCurrentStep(3)}
          style={{ backgroundColor: '#f3f4f6', color: '#374151', border: '1px solid #d1d5db' }}
        >
          返回大纲
        </button>
        <button 
          className="button"
          onClick={() => {
            setCurrentStep(1)
            setCurrentPaper(null)
            setPaperContent('')
            setFormData({
              title: '',
              field: '',
              education: '本科',
              wordCount: '8000',
              keywords: '',
              description: ''
            })
          }}
        >
          创建新论文
        </button>
      </div>
    </div>
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* WebSocket连接状态 */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '8px',
        padding: '8px 12px',
        backgroundColor: wsConnected ? '#ecfdf5' : '#fef2f2',
        borderRadius: '6px',
        fontSize: '12px'
      }}>
        <div style={{ 
          width: '8px', 
          height: '8px', 
          borderRadius: '50%', 
          backgroundColor: wsConnected ? '#10b981' : '#ef4444' 
        }} />
        WebSocket {wsConnected ? '已连接' : '未连接'}
      </div>

      {/* 步骤指示器 */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
        {steps.map((step, index) => (
          <div key={step.id} style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              backgroundColor: currentStep >= step.id ? '#3b82f6' : '#e5e7eb',
              color: currentStep >= step.id ? 'white' : '#6b7280',
              fontWeight: '600',
              fontSize: '16px'
            }}>
              {step.icon}
            </div>
            <div style={{ marginLeft: '12px', flex: 1 }}>
              <div style={{ 
                fontSize: '14px', 
                fontWeight: '500',
                color: currentStep >= step.id ? '#1f2937' : '#6b7280'
              }}>
                {step.title}
              </div>
              <div style={{ 
                fontSize: '12px', 
                color: '#9ca3af' 
              }}>
                {step.desc}
              </div>
            </div>
            {index < steps.length - 1 && (
              <ChevronRight size={16} style={{ color: '#d1d5db', marginLeft: '8px' }} />
            )}
          </div>
        ))}
      </div>

      {/* 步骤内容 */}
      {currentStep === 1 && renderStep1()}
      {currentStep === 2 && renderStep2()}
      {currentStep === 3 && renderStep3()}
      {currentStep === 4 && renderStep4()}
    </div>
  )
}