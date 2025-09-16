import { useState, useEffect } from 'react'
import { 
  Search, Upload, Lightbulb, Clock, FileText, Download, ChevronRight, CheckCircle,
  BarChart3, Image, Table, PieChart, Settings, RefreshCw, Check, X
} from 'lucide-react'

const API_BASE_URL = 'https://5001-i362990uh7vzwuu0d0o9j-6532622b.e2b.dev'

export function PaperForm() {
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState({
    // 基本信息
    title: '',
    field: '',
    education: '本科',
    wordCount: '8000',
    language: 'zh',
    format: 'standard',
    keywords: '',
    description: '',
    // 参考文献
    customReferences: '',
    selectedReferences: [],
    // 大纲
    outline: null,
    chartOptions: {}
  })

  const [isGenerating, setIsGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [wsConnected, setWsConnected] = useState(false)
  const [recommendedReferences, setRecommendedReferences] = useState([])
  const [outlineData, setOutlineData] = useState(null)
  const [finalPaper, setFinalPaper] = useState(null)
  const [editingOutline, setEditingOutline] = useState(false)
  const [searchingReferences, setSearchingReferences] = useState(false)
  const [orderInfo, setOrderInfo] = useState(null)
  const [showOrderModal, setShowOrderModal] = useState(false)

  // 模拟WebSocket连接状态
  useEffect(() => {
    setWsConnected(true)
  }, [])

  // 教育层次选项
  const educationOptions = [
    { value: '专科', label: '专科' },
    { value: '本科', label: '本科' },
    { value: '硕士', label: '硕士' },
    { value: '博士', label: '博士' }
  ]

  // 论文字数选项
  const wordCountOptions = [
    { value: '3000', label: '3000字' },
    { value: '5000', label: '5000字' },
    { value: '8000', label: '8000字' },
    { value: '10000', label: '10000字' },
    { value: '15000', label: '15000字' },
    { value: '20000', label: '20000字' }
  ]

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleNextStep = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  // 搜索推荐文献
  const generateRecommendedReferences = async () => {
    if (!formData.title && !formData.field) {
      alert('请先输入论文标题或研究领域')
      return
    }

    try {
      setSearchingReferences(true)
      
      // 调用后端API搜索文献
      const response = await fetch(`${API_BASE_URL}/api/thesis/search-references`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          query: formData.title || formData.field,
          field: formData.field,
          education_level: formData.education,
          limit: 8
        })
      })

      const data = await response.json()
      
      if (data.success && data.data) {
        // 为搜索结果添加选中状态
        const referencesWithSelection = data.data.map((ref) => ({
          ...ref,
          selected: false,
          tags: ref.tags || []
        }))
        setRecommendedReferences(referencesWithSelection)
      } else {
        // 如果API失败，使用模拟推荐文献数据
      const mockReferences = [
        {
          id: 1,
          title: `提升职业本科院校教师教育力的途径探索(1)——以大学生学科竞赛力载体`,
          authors: '黄敏, 章正伟, 吴敏华, 林长红',
          journal: '现代职业教育',
          year: '2025',
          tags: ['职业本科', '教师教育力', '学科竞赛', '教育改革', '教学质量'],
          selected: false
        },
        {
          id: 2,
          title: '吴旭干："申江1号"能够提早上市！成蟹养殖成活率能达到60%～70%',
          authors: '彭可欣',
          journal: '当代水产',
          year: '2025',
          tags: [],
          selected: false
        },
        {
          id: 3,
          title: 'ERAS联合"互联网+延续性护理"在1例双侧全髋关节置换术患者中的应用效果',
          authors: '廖秋侠, 周美含, 莫伟, 古云师, 刘方印',
          journal: '临床医学研究与实践',
          year: '2025',
          tags: ['加速康复外科', '"互联网+延续性护理"', '联合书法现代护理', '全髋关节置换术', 'Tanner分期'],
          selected: false
        },
        {
          id: 4,
          title: '特发性中枢性早熟女童IGF-1、IGFBP-3与Tanner分期的关系',
          authors: '罗婷婷, 李茜, 陈婷, 何珊',
          journal: '中国医学创新',
          year: '2025',
          tags: ['社会工作者评价体系', '顾客导向解决方案心理', '获动评估实证法了', 'Tanner分期'],
          selected: false
        }
      ]
      
        setRecommendedReferences(mockReferences.map(ref => ({ ...ref, selected: false })))
      }
    } catch (error) {
      console.error('搜索文献失败:', error)
      alert('搜索文献失败，请检查网络连接')
    } finally {
      setSearchingReferences(false)
    }
  }

  // 全选/取消全选文献
  const toggleAllReferences = () => {
    const hasUnselected = recommendedReferences.some(ref => !ref.selected)
    setRecommendedReferences(prev => 
      prev.map(ref => ({ ...ref, selected: hasUnselected }))
    )
  }

  // 下载论文
  const downloadPaper = async () => {
    if (!finalPaper || !finalPaper.id) {
      alert('论文数据无效，无法下载')
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/thesis/download/${finalPaper.id}`, {
        method: 'GET',
        credentials: 'include'
      })

      if (response.ok) {
        // 创建下载链接
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${finalPaper.title || '论文'}.docx`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        
        alert('论文下载成功！')
      } else {
        const errorData = await response.json()
        alert(errorData.message || '下载失败')
      }
    } catch (error) {
      console.error('下载论文失败:', error)
      alert('下载失败，请检查网络连接')
    }
  }

  // 创建订单
  const createOrder = async (paperData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/orders/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          product_type: 'paper',
          product_name: `论文写作：${paperData.title}`,
          paper_config: {
            title: paperData.title,
            field: paperData.field,
            education_level: paperData.education,
            word_count: paperData.wordCount,
            keywords: paperData.keywords,
            description: paperData.description
          },
          original_price: getPaperPrice(paperData.education, paperData.wordCount),
          actual_price: getPaperPrice(paperData.education, paperData.wordCount)
        })
      })
      
      const data = await response.json()
      if (data.success) {
        setOrderInfo(data.data)
        return data.data
      } else {
        throw new Error(data.message)
      }
    } catch (error) {
      console.error('创建订单失败:', error)
      throw error
    }
  }

  // 获取论文价格
  const getPaperPrice = (education, wordCount) => {
    const basePrice = {
      '专科': 0.15,
      '本科': 0.20,
      '硕士': 0.25,
      '博士': 0.30
    }
    const pricePerWord = basePrice[education] || 0.20
    return Math.round(parseInt(wordCount) * pricePerWord)
  }

  // 生成论文（集成订单系统）
  const generatePaper = async () => {
    if (!formData.title || !formData.field) {
      alert('请填写论文标题和研究领域')
      return
    }

    try {
      setIsGenerating(true)
      setGenerationProgress(10)

      // 1. 创建订单
      const order = await createOrder(formData)
      setGenerationProgress(20)

      // 2. 创建论文记录
      const createResponse = await fetch(`${API_BASE_URL}/api/thesis/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          title: formData.title,
          field: formData.field,
          education_level: formData.education,
          keywords: formData.keywords,
          description: formData.description,
          word_count: parseInt(formData.wordCount),
          order_id: order.id
        })
      })

      const createData = await createResponse.json()
      if (!createData.success) {
        throw new Error(createData.message)
      }

      setGenerationProgress(40)

      // 3. 生成论文内容
      const generateResponse = await fetch(`${API_BASE_URL}/api/thesis/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          paper_id: createData.data.paper_id,
          outline: outlineData?.structured,
          references: recommendedReferences.filter(ref => ref.selected)
        })
      })

      const generateData = await generateResponse.json()
      if (generateData.success) {
        const paper = {
          id: createData.data.paper_id,
          title: formData.title,
          content: generateData.data.content,
          word_count: generateData.data.word_count,
          status: 'completed',
          order_id: order.id,
          order_no: order.order_no,
          wordCount: generateData.data.word_count,
          createdAt: new Date().toLocaleString()
        }
        
        setFinalPaper(paper)
        setGenerationProgress(100)
        
        // 更新订单状态
        await updateOrderStatus(order.id, 'completed', paper.id)
        
        alert('论文生成完成！')
      } else {
        throw new Error(generateData.message)
      }
    } catch (error) {
      console.error('生成论文失败:', error)
      alert(`生成论文失败: ${error.message}`)
      setGenerationProgress(0)
    } finally {
      setIsGenerating(false)
    }
  }

  // 更新订单状态
  const updateOrderStatus = async (orderId, status, paperId = null) => {
    try {
      await fetch(`${API_BASE_URL}/api/orders/${orderId}/update`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          status: status,
          paper_id: paperId
        })
      })
    } catch (error) {
      console.error('更新订单状态失败:', error)
    }
  }

  // 预览论文
  const previewPaper = () => {
    if (!finalPaper || !finalPaper.content) {
      alert('暂无论文内容可预览')
      return
    }
    
    // 创建预览窗口
    const previewWindow = window.open('', '_blank', 'width=800,height=600,scrollbars=yes')
    if (previewWindow) {
      previewWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>${finalPaper.title}</title>
          <style>
            body { font-family: "Times New Roman", serif; margin: 40px; line-height: 1.6; }
            h1 { text-align: center; font-size: 24px; margin-bottom: 30px; }
            h2 { font-size: 18px; margin-top: 25px; margin-bottom: 10px; }
            p { text-indent: 2em; margin-bottom: 12px; }
            .meta { text-align: center; color: #666; margin-bottom: 30px; }
          </style>
        </head>
        <body>
          <h1>${finalPaper.title}</h1>
          <div class="meta">
            字数：${finalPaper.wordCount}字 | 生成时间：${finalPaper.createdAt}
            ${finalPaper.order_no ? `<br>订单号：${finalPaper.order_no} | 论文ID：${finalPaper.id}` : ''}
          </div>
          <div>${finalPaper.content.replace(/\n/g, '<br>')}</div>
        </body>
        </html>
      `)
      previewWindow.document.close()
    }
  }

  // 选择/取消推荐文献
  const toggleReference = (refId) => {
    setRecommendedReferences(prev => 
      prev.map(ref => 
        ref.id === refId ? { ...ref, selected: !ref.selected } : ref
      )
    )
  }

  // 生成大纲
  const generateOutline = async () => {
    try {
      setIsGenerating(true)
      // 模拟大纲数据
      const mockOutline = {
        structured: [
          { 
            id: 1, 
            title: '1. 绪论', 
            children: [
              { id: 11, title: '1.1 研究背景', hasChart: false, chartType: null },
              { id: 12, title: '1.2 研究意义', hasChart: false, chartType: null },
              { id: 13, title: '1.3 研究内容', hasChart: false, chartType: null }
            ]
          },
          { 
            id: 2, 
            title: '2. 相关理论基础', 
            children: [
              { id: 21, title: '2.1 理论概述', hasChart: false, chartType: null },
              { id: 22, title: '2.2 技术发展现状', hasChart: true, chartType: 'table' }
            ]
          },
          { 
            id: 3, 
            title: '3. 研究方法与设计', 
            children: [
              { id: 31, title: '3.1 研究方法', hasChart: false, chartType: null },
              { id: 32, title: '3.2 实验设计', hasChart: true, chartType: 'chart' },
              { id: 33, title: '3.3 数据采集', hasChart: false, chartType: null }
            ]
          },
          { 
            id: 4, 
            title: '4. 结果分析', 
            children: [
              { id: 41, title: '4.1 数据分析结果', hasChart: true, chartType: 'chart' },
              { id: 42, title: '4.2 结果讨论', hasChart: false, chartType: null }
            ]
          },
          { 
            id: 5, 
            title: '5. 结论与展望', 
            children: [
              { id: 51, title: '5.1 研究结论', hasChart: false, chartType: null },
              { id: 52, title: '5.2 研究展望', hasChart: false, chartType: null }
            ]
          }
        ],
        systemRecommended: `
        一、绪论
        1.1 研究背景与意义
        1.2 国内外研究现状
        1.3 研究目标与内容
        1.4 研究方法与技术路线
        
        二、相关理论与技术基础
        2.1 基础理论概述
        2.2 关键技术分析
        2.3 发展趋势研究
        
        三、系统设计与实现
        3.1 需求分析
        3.2 系统架构设计
        3.3 核心算法设计
        3.4 系统实现
        
        四、实验结果与分析
        4.1 实验环境与数据
        4.2 实验结果分析
        4.3 性能评估
        
        五、总结与展望
        5.1 研究总结
        5.2 存在的不足
        5.3 未来工作展望
        `
      }
      
      setOutlineData(mockOutline)
      setIsGenerating(false)
    } catch (error) {
      console.error('生成大纲失败:', error)
      setIsGenerating(false)
    }
  }

  // 编辑章节标题
  const editSectionTitle = (sectionId, newTitle) => {
    setOutlineData(prev => {
      if (!prev) return prev
      
      const newStructured = prev.structured.map(section => {
        if (section.id === sectionId) {
          return { ...section, title: newTitle }
        }
        
        return {
          ...section,
          children: section.children.map(child => {
            if (child.id === sectionId) {
              return { ...child, title: newTitle }
            }
            return child
          })
        }
      })
      
      return {
        ...prev,
        structured: newStructured
      }
    })
  }

  // 添加新章节
  const addNewSection = () => {
    setOutlineData(prev => {
      if (!prev) return prev
      
      const maxId = Math.max(...prev.structured.map(s => s.id), ...prev.structured.flatMap(s => s.children.map(c => c.id)))
      const newSectionId = maxId + 1
      
      const newSection = {
        id: newSectionId,
        title: `${prev.structured.length + 1}. 新章节`,
        children: [
          { id: newSectionId + 1, title: `${prev.structured.length + 1}.1 子章节`, hasChart: false, chartType: null }
        ]
      }
      
      return {
        ...prev,
        structured: [...prev.structured, newSection]
      }
    })
  }

  // 添加子章节
  const addSubSection = (parentId) => {
    setOutlineData(prev => {
      if (!prev) return prev
      
      const maxId = Math.max(...prev.structured.map(s => s.id), ...prev.structured.flatMap(s => s.children.map(c => c.id)))
      
      const newStructured = prev.structured.map(section => {
        if (section.id === parentId) {
          const newSubId = maxId + 1
          const newSub = {
            id: newSubId,
            title: `${section.title.split('.')[0]}.${section.children.length + 1} 新子章节`,
            hasChart: false,
            chartType: null
          }
          return {
            ...section,
            children: [...section.children, newSub]
          }
        }
        return section
      })
      
      return {
        ...prev,
        structured: newStructured
      }
    })
  }

  // 删除章节
  const deleteSection = (sectionId) => {
    setOutlineData(prev => {
      if (!prev) return prev
      
      // 删除主章节
      let newStructured = prev.structured.filter(section => section.id !== sectionId)
      
      // 删除子章节
      newStructured = newStructured.map(section => ({
        ...section,
        children: section.children.filter(child => child.id !== sectionId)
      }))
      
      return {
        ...prev,
        structured: newStructured
      }
    })
  }

  // 切换章节图表选项
  const toggleChartOption = (sectionId, chartType) => {
    setOutlineData(prev => {
      if (!prev) return prev
      
      const newStructured = prev.structured.map(section => ({
        ...section,
        children: section.children.map(child => {
          if (child.id === sectionId) {
            return {
              ...child,
              hasChart: chartType ? true : false,
              chartType: chartType
            }
          }
          return child
        })
      }))
      
      return {
        ...prev,
        structured: newStructured
      }
    })
  }

  // 生成最终论文（使用集成订单系统）
  const generateFinalPaper = generatePaper

  // 步骤指示器
  // 步骤切换函数
  const goToStep = (step) => {
    // 只能切换到已完成的步骤或下一步
    if (step <= currentStep || step === currentStep + 1) {
      setCurrentStep(step)
    }
  }

  const StepIndicator = () => (
    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '32px' }}>
      {[1, 2, 3, 4].map((step, index) => (
        <div key={step} style={{ display: 'flex', alignItems: 'center' }}>
          <button 
            onClick={() => goToStep(step)}
            disabled={step > currentStep + 1}
            style={{ 
              width: '32px', 
              height: '32px', 
              borderRadius: '50%', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              backgroundColor: step <= currentStep ? '#3b82f6' : '#e5e7eb',
              color: step <= currentStep ? 'white' : '#6b7280',
              fontWeight: '500',
              border: 'none',
              cursor: step <= currentStep || step === currentStep + 1 ? 'pointer' : 'not-allowed',
              transition: 'all 0.2s ease',
              opacity: step > currentStep + 1 ? 0.5 : 1
            }}
            onMouseOver={(e) => {
              if (step <= currentStep || step === currentStep + 1) {
                e.target.style.transform = 'scale(1.1)'
              }
            }}
            onMouseOut={(e) => {
              e.target.style.transform = 'scale(1)'
            }}
          >
            {step < currentStep ? <Check size={16} /> : step}
          </button>
          {index < 3 && (
            <div 
              style={{ 
                width: '60px', 
                height: '2px', 
                backgroundColor: step < currentStep ? '#3b82f6' : '#e5e7eb',
                margin: '0 16px'
              }} 
            />
          )}
        </div>
      ))}
    </div>
  )

  // 基本信息表单
  const BasicInfoForm = () => (
    <div>
      <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px' }}>论文基本信息</h2>
      
      {/* 论文标题 */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
          <span style={{ color: '#dc2626' }}>*</span> 论文标题：
        </label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => handleInputChange('title', e.target.value)}
          placeholder="请输入论文标题"
          style={{
            width: '100%',
            padding: '12px 16px',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            fontSize: '14px'
          }}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        {/* 学历 */}
        <div>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
            <span style={{ color: '#dc2626' }}>*</span> 学历：
          </label>
          <select
            value={formData.education}
            onChange={(e) => handleInputChange('education', e.target.value)}
            style={{
              width: '100%',
              padding: '12px 16px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '14px',
              backgroundColor: 'white'
            }}
          >
            {educationOptions.map(option => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </div>

        {/* 论文字数 */}
        <div>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
            <span style={{ color: '#dc2626' }}>*</span> 论文字数：
          </label>
          <select
            value={formData.wordCount}
            onChange={(e) => handleInputChange('wordCount', e.target.value)}
            style={{
              width: '100%',
              padding: '12px 16px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '14px',
              backgroundColor: 'white'
            }}
          >
            {wordCountOptions.map(option => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* 语言选择 */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '12px' }}>
          语言：
        </label>
        <div style={{ display: 'flex', gap: '16px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input
              type="radio"
              name="language"
              value="zh"
              checked={formData.language === 'zh'}
              onChange={(e) => handleInputChange('language', e.target.value)}
            />
            中文
          </label>
        </div>
      </div>

      {/* 图表公式选择 */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '12px' }}>
          图表公式：
        </label>
        <div style={{ display: 'flex', gap: '16px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input
              type="radio"
              name="format"
              value="standard"
              checked={formData.format === 'standard'}
              onChange={(e) => handleInputChange('format', e.target.value)}
            />
            图表/公式/代码
          </label>
        </div>
      </div>

      {/* 补充说明 */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>
          补充说明：
        </label>
        <textarea
          value={formData.description}
          onChange={(e) => handleInputChange('description', e.target.value)}
          placeholder="补充说明..."
          rows={4}
          style={{
            width: '100%',
            padding: '12px 16px',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            fontSize: '14px',
            resize: 'vertical'
          }}
        />
        <div style={{ textAlign: 'right', fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
          {formData.description.length}/1500
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button
          onClick={() => alert('开题报告功能开发中')}
          style={{
            padding: '12px 24px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: 'pointer'
          }}
        >
          上传开题报告
        </button>
        
        <button
          onClick={handleNextStep}
          disabled={!formData.title}
          style={{
            padding: '12px 24px',
            backgroundColor: formData.title ? '#3b82f6' : '#9ca3af',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: formData.title ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          智能选题 <ChevronRight size={16} />
        </button>
      </div>
    </div>
  )

  // 参考文献界面
  const ReferencesForm = () => (
    <div>
      <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px' }}>参考文献</h2>
      
      {/* 自定义文献输入 */}
      <div style={{ marginBottom: '32px' }}>
        <h3 style={{ fontSize: '16px', fontWeight: '500', marginBottom: '12px' }}>
          输入自定义参考文献，选择推荐文献重新（引文格式）
        </h3>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
          <textarea
            value={formData.customReferences}
            onChange={(e) => handleInputChange('customReferences', e.target.value)}
            placeholder="自定义输入文献（本科参考文献15个以上，硕士20个以上，博士30个以上）"
            rows={6}
            style={{
              flex: 1,
              padding: '12px 16px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '14px',
              resize: 'vertical'
            }}
          />
          <button
            style={{
              padding: '12px 20px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              whiteSpace: 'nowrap'
            }}
          >
            解析文献文献格式
          </button>
        </div>
        <div style={{ color: '#dc2626', fontSize: '12px', marginTop: '8px' }}>
          ⚠️ 注意中英文标点，需确保引用文献
        </div>
      </div>

      {/* 推荐文献 */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '500' }}>推荐文献</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#6b7280' }}>
            <Settings size={14} />
            本科参考文献15个以上，硕士20个以上，博士30个以上
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={generateRecommendedReferences}
              disabled={searchingReferences}
              style={{
                padding: '8px 16px',
                backgroundColor: searchingReferences ? '#9ca3af' : '#dc2626',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '12px',
                cursor: searchingReferences ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Search size={12} />
              {searchingReferences ? '搜索中...' : '智能搜索文献'}
              {searchingReferences && <RefreshCw size={12} className="animate-spin" />}
            </button>
            {recommendedReferences.length > 0 && (
              <button
                onClick={toggleAllReferences}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  fontSize: '12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <Check size={12} />
                {recommendedReferences.every(ref => ref.selected) ? '取消全选' : '全选文献'}
              </button>
            )}
          </div>
        </div>

        {/* 推荐文献列表 */}
        <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px' }}>
          {recommendedReferences.map((ref, index) => (
            <div 
              key={ref.id}
              style={{ 
                padding: '16px',
                borderBottom: index < recommendedReferences.length - 1 ? '1px solid #e5e7eb' : 'none',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px'
              }}
            >
              <input
                type="checkbox"
                checked={ref.selected}
                onChange={() => toggleReference(ref.id)}
                style={{ marginTop: '4px' }}
              />
              <div style={{ flex: 1 }}>
                <h4 style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', color: '#1f2937' }}>
                  {ref.title}
                </h4>
                <p style={{ fontSize: '13px', color: '#6b7280', marginBottom: '8px' }}>
                  {ref.authors} | {ref.journal} | {ref.year}
                </p>
                {ref.tags.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {ref.tags.map((tag, tagIndex) => (
                      <span
                        key={tagIndex}
                        style={{
                          padding: '2px 8px',
                          backgroundColor: '#dbeafe',
                          color: '#1d4ed8',
                          fontSize: '11px',
                          borderRadius: '4px'
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {recommendedReferences.length === 0 && (
            <div style={{ padding: '48px', textAlign: 'center', color: '#6b7280' }}>
              <Search size={32} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
              <p>点击"追加文献"获取推荐文献</p>
            </div>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <button
          onClick={handlePrevStep}
          style={{
            padding: '12px 24px',
            backgroundColor: 'white',
            color: '#374151',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: 'pointer'
          }}
        >
          上一步
        </button>
        <button
          onClick={handleNextStep}
          style={{
            padding: '12px 24px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            fontWeight: '500',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          下一步 <ChevronRight size={16} />
        </button>
      </div>
    </div>
  )

  // 智能大纲界面
  const OutlineForm = () => (
    <div>
      <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px' }}>智能大纲</h2>
      
      {!outlineData ? (
        <div style={{ textAlign: 'center', padding: '48px 0' }}>
          <Lightbulb size={48} style={{ margin: '0 auto 16px', color: '#f59e0b' }} />
          <p style={{ fontSize: '16px', color: '#6b7280', marginBottom: '24px' }}>
            点击生成大纲开始创建论文结构
          </p>
          <button
            onClick={generateOutline}
            disabled={isGenerating}
            style={{
              padding: '12px 32px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '500',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              margin: '0 auto'
            }}
          >
            {isGenerating ? (
              <>
                <RefreshCw size={16} className="animate-spin" />
                生成中...
              </>
            ) : (
              '生成大纲'
            )}
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
          {/* 结构提纲 */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: '500', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={16} />
                结构提纲
              </h3>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => setEditingOutline(!editingOutline)}
                  style={{
                    padding: '6px 12px',
                    backgroundColor: editingOutline ? '#dc2626' : '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '12px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  {editingOutline ? (
                    <>
                      <X size={12} />
                      完成编辑
                    </>
                  ) : (
                    <>
                      <FileText size={12} />
                      编辑大纲
                    </>
                  )}
                </button>
                {editingOutline && (
                  <button
                    onClick={addNewSection}
                    style={{
                      padding: '6px 12px',
                      backgroundColor: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      fontSize: '12px',
                      cursor: 'pointer'
                    }}
                  >
                    + 新增章节
                  </button>
                )}
              </div>
            </div>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '16px', backgroundColor: '#f9fafb' }}>
              {outlineData.structured.map((section) => (
                <div key={section.id} style={{ marginBottom: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    {editingOutline ? (
                      <input
                        type="text"
                        value={section.title}
                        onChange={(e) => editSectionTitle(section.id, e.target.value)}
                        style={{
                          fontSize: '14px',
                          fontWeight: '600',
                          color: '#1f2937',
                          border: '1px solid #d1d5db',
                          borderRadius: '4px',
                          padding: '4px 8px',
                          flex: 1,
                          marginRight: '8px'
                        }}
                      />
                    ) : (
                      <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#1f2937', flex: 1 }}>
                        {section.title}
                      </h4>
                    )}
                    {editingOutline && (
                      <div style={{ display: 'flex', gap: '4px' }}>
                        <button
                          onClick={() => addSubSection(section.id)}
                          style={{
                            padding: '2px 6px',
                            backgroundColor: '#10b981',
                            color: 'white',
                            border: 'none',
                            borderRadius: '3px',
                            fontSize: '10px',
                            cursor: 'pointer'
                          }}
                        >
                          +子章节
                        </button>
                        <button
                          onClick={() => deleteSection(section.id)}
                          style={{
                            padding: '2px 6px',
                            backgroundColor: '#dc2626',
                            color: 'white',
                            border: 'none',
                            borderRadius: '3px',
                            fontSize: '10px',
                            cursor: 'pointer'
                          }}
                        >
                          删除
                        </button>
                      </div>
                    )}
                  </div>
                  {section.children.map((child) => (
                    <div key={child.id} style={{ marginLeft: '16px', marginBottom: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      {editingOutline ? (
                        <input
                          type="text"
                          value={child.title}
                          onChange={(e) => editSectionTitle(child.id, e.target.value)}
                          style={{
                            fontSize: '13px',
                            color: '#6b7280',
                            border: '1px solid #d1d5db',
                            borderRadius: '3px',
                            padding: '2px 6px',
                            flex: 1,
                            marginRight: '8px'
                          }}
                        />
                      ) : (
                        <span style={{ fontSize: '13px', color: '#6b7280', flex: 1 }}>{child.title}</span>
                      )}
                      <div style={{ display: 'flex', gap: '4px' }}>
                        {editingOutline && (
                          <button
                            onClick={() => deleteSection(child.id)}
                            style={{
                              padding: '1px 4px',
                              backgroundColor: '#dc2626',
                              color: 'white',
                              border: 'none',
                              borderRadius: '2px',
                              fontSize: '9px',
                              cursor: 'pointer'
                            }}
                          >
                            删除
                          </button>
                        )}
                        <button
                          onClick={() => toggleChartOption(child.id, child.chartType === 'table' ? null : 'table')}
                          style={{
                            padding: '4px 8px',
                            backgroundColor: child.chartType === 'table' ? '#3b82f6' : '#e5e7eb',
                            color: child.chartType === 'table' ? 'white' : '#6b7280',
                            border: 'none',
                            borderRadius: '4px',
                            fontSize: '10px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '2px'
                          }}
                        >
                          <Table size={10} />
                          表格
                        </button>
                        <button
                          onClick={() => toggleChartOption(child.id, child.chartType === 'chart' ? null : 'chart')}
                          style={{
                            padding: '4px 8px',
                            backgroundColor: child.chartType === 'chart' ? '#3b82f6' : '#e5e7eb',
                            color: child.chartType === 'chart' ? 'white' : '#6b7280',
                            border: 'none',
                            borderRadius: '4px',
                            fontSize: '10px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '2px'
                          }}
                        >
                          <BarChart3 size={10} />
                          图表
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* 系统推荐提纲 */}
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: '500', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Settings size={16} />
              系统推荐提纲
            </h3>
            <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '16px', backgroundColor: '#f9fafb' }}>
              <pre style={{ 
                fontSize: '13px', 
                lineHeight: '1.5', 
                color: '#374151',
                whiteSpace: 'pre-wrap',
                margin: 0,
                fontFamily: 'ui-monospace, "Cascadia Code", "Source Code Pro", Menlo, consolas, monospace'
              }}>
                {outlineData.systemRecommended}
              </pre>
            </div>
          </div>
        </div>
      )}

      {outlineData && (
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px' }}>
          <button
            onClick={handlePrevStep}
            style={{
              padding: '12px 24px',
              backgroundColor: 'white',
              color: '#374151',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            上一步
          </button>
          <button
            onClick={handleNextStep}
            style={{
              padding: '12px 24px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            生成论文 <ChevronRight size={16} />
          </button>
        </div>
      )}
    </div>
  )

  // 生成下载界面
  const GenerateForm = () => (
    <div>
      <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px' }}>生成论文</h2>
      
      {!finalPaper ? (
        <div>
          {isGenerating ? (
            <div style={{ textAlign: 'center', padding: '48px 0' }}>
              <div style={{ 
                width: '80px', 
                height: '80px', 
                border: '4px solid #e5e7eb', 
                borderTop: '4px solid #3b82f6',
                borderRadius: '50%',
                margin: '0 auto 24px',
                animation: 'spin 1s linear infinite'
              }} />
              <p style={{ fontSize: '18px', fontWeight: '500', marginBottom: '8px' }}>正在生成论文...</p>
              <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '16px' }}>
                请耐心等待，预计需要2-3分钟
              </p>
              <div style={{ width: '300px', height: '8px', backgroundColor: '#e5e7eb', borderRadius: '4px', margin: '0 auto', overflow: 'hidden' }}>
                <div 
                  style={{ 
                    width: `${generationProgress}%`, 
                    height: '100%', 
                    backgroundColor: '#3b82f6',
                    transition: 'width 0.3s ease'
                  }} 
                />
              </div>
              <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '8px' }}>
                进度: {generationProgress}%
              </p>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '48px 0' }}>
              <FileText size={48} style={{ margin: '0 auto 16px', color: '#3b82f6' }} />
              <p style={{ fontSize: '16px', color: '#6b7280', marginBottom: '24px' }}>
                准备生成完整论文
              </p>
              <div style={{ backgroundColor: '#f3f4f6', padding: '20px', borderRadius: '8px', marginBottom: '24px', textAlign: 'left' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '500', marginBottom: '12px' }}>论文信息摘要：</h4>
                <p style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>标题：{formData.title}</p>
                <p style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>学历：{formData.education}</p>
                <p style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>字数：{formData.wordCount}字</p>
                <p style={{ fontSize: '13px', color: '#6b7280' }}>已选择推荐文献：{recommendedReferences.filter(r => r.selected).length}篇</p>
              </div>
              <button
                onClick={generateFinalPaper}
                style={{
                  padding: '16px 32px',
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  margin: '0 auto'
                }}
              >
                开始生成论文
              </button>
            </div>
          )}
        </div>
      ) : (
        <div>
          <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '16px', marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <CheckCircle size={20} style={{ color: '#16a34a' }} />
              <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#16a34a' }}>论文生成完成！</h3>
            </div>
            <p style={{ fontSize: '14px', color: '#15803d' }}>
              论文已成功生成，您可以预览内容或直接下载。
            </p>
          </div>

          <div style={{ border: '1px solid #e5e7eb', borderRadius: '8px', padding: '20px', marginBottom: '24px' }}>
            <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>{finalPaper.title}</h4>
            <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '16px' }}>
              字数：{finalPaper.wordCount}字 | 生成时间：{finalPaper.createdAt}
            </div>
            <div style={{ 
              maxHeight: '300px', 
              overflow: 'auto', 
              backgroundColor: '#f9fafb', 
              padding: '16px', 
              borderRadius: '6px',
              fontSize: '14px',
              lineHeight: '1.6'
            }}>
              {finalPaper.content}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <button
              onClick={downloadPaper}
              style={{
                padding: '12px 24px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <Download size={16} />
              下载论文(Word)
            </button>
            <button
              onClick={previewPaper}
              style={{
                padding: '12px 24px',
                backgroundColor: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <FileText size={16} />
              预览论文
            </button>
            <button
              onClick={() => {
                setFinalPaper(null)
                setCurrentStep(1)
              }}
              style={{
                padding: '12px 24px',
                backgroundColor: 'white',
                color: '#374151',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <RefreshCw size={16} />
              重新生成
            </button>
          </div>
        </div>
      )}

      {!isGenerating && !finalPaper && (
        <div style={{ display: 'flex', justifyContent: 'flex-start', marginTop: '32px' }}>
          <button
            onClick={handlePrevStep}
            style={{
              padding: '12px 24px',
              backgroundColor: 'white',
              color: '#374151',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            上一步
          </button>
        </div>
      )}
    </div>
  )

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return <BasicInfoForm />
      case 2:
        return <ReferencesForm />
      case 3:
        return <OutlineForm />
      case 4:
        return <GenerateForm />
      default:
        return <BasicInfoForm />
    }
  }

  return (
    <div>
      {/* WebSocket连接状态 */}
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '8px', 
        marginBottom: '20px',
        padding: '8px 12px',
        backgroundColor: wsConnected ? '#f0fdf4' : '#fef2f2',
        border: `1px solid ${wsConnected ? '#bbf7d0' : '#fecaca'}`,
        borderRadius: '6px',
        fontSize: '12px'
      }}>
        <div style={{ 
          width: '8px', 
          height: '8px', 
          borderRadius: '50%', 
          backgroundColor: wsConnected ? '#16a34a' : '#dc2626' 
        }} />
        WebSocket {wsConnected ? '已连接' : '未连接'}
      </div>

      <StepIndicator />
      
      <div className="card" style={{ padding: '32px' }}>
        {renderCurrentStep()}
      </div>
    </div>
  )
}