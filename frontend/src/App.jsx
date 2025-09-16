import { useState } from 'react'
import { 
  Search, 
  FileText, 
  ArrowDown, 
  Book, 
  FilePlus, 
  FileSpreadsheet, 
  Flame, 
  FileCheck, 
  FileImage, 
  BarChart, 
  HelpCircle, 
  Code, 
  User, 
  Bot
} from 'lucide-react'
import { PaperForm } from './PaperForm.jsx'
import { ChatWindow } from './ChatWindow.jsx'
import { UserCenter } from './UserCenter.jsx'
import { TestComponent } from './TestComponent.jsx'

function App() {
  const [selectedMenuItem, setSelectedMenuItem] = useState('毕业论文')

  const menuItems = [
    { icon: Search, label: '订单查询' },
    { icon: FileText, label: '毕业论文', active: true },
    { icon: ArrowDown, label: '降重/降AI' },
    { icon: Book, label: '文献综述' },
    { icon: FilePlus, label: '开题报告' },
    { icon: FileSpreadsheet, label: '期刊论文' },
    { icon: Flame, label: '限时优惠' },
    { icon: FileSpreadsheet, label: 'PPT' },
    { icon: FileCheck, label: '任务书' },
    { icon: FileImage, label: '实践报告' },
    { icon: BarChart, label: '数据分析' },
    { icon: HelpCircle, label: '问卷调查' },
    { icon: Code, label: '源码宝库' },
    { icon: User, label: '用户中心' },
    { icon: Bot, label: '人工排版' }
  ]

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      {/* 左侧导航 */}
      <aside style={{ width: '208px', backgroundColor: 'white', borderRight: '1px solid #e5e7eb', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)' }}>
        <div style={{ padding: '16px' }}>
          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
            <div style={{ width: '32px', height: '32px', backgroundColor: '#3b82f6', borderRadius: '4px', marginRight: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>
              B
            </div>
            <span style={{ fontSize: '20px', fontWeight: '600', color: '#1f2937' }}>百考通</span>
          </div>
          
          {/* 菜单项 */}
          <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {menuItems.map((item, index) => {
              const Icon = item.icon
              const isActive = item.label === selectedMenuItem
              return (
                <button
                  key={index}
                  onClick={() => setSelectedMenuItem(item.label)}
                  className="button"
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    padding: '8px 12px',
                    fontSize: '14px',
                    borderRadius: '6px',
                    border: 'none',
                    cursor: 'pointer',
                    backgroundColor: isActive ? '#dbeafe' : 'transparent',
                    color: isActive ? '#2563eb' : '#374151',
                    borderWidth: isActive ? '1px' : '0',
                    borderStyle: 'solid',
                    borderColor: isActive ? '#93c5fd' : 'transparent'
                  }}
                  onMouseOver={(e) => {
                    if (!isActive) e.target.style.backgroundColor = '#f3f4f6'
                  }}
                  onMouseOut={(e) => {
                    if (!isActive) e.target.style.backgroundColor = 'transparent'
                  }}
                >
                  <Icon size={16} style={{ marginRight: '12px' }} />
                  {item.label}
                </button>
              )
            })}
          </nav>
        </div>
      </aside>

      {/* 主内容区域 */}
      <main style={{ flex: 1, padding: '24px' }}>
        {/* 顶部标题栏 */}
        <header className="card" style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h1 style={{ fontSize: '24px', fontWeight: '600', color: '#1f2937' }}>{selectedMenuItem}</h1>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button className="button">
                输入完整的文章标题，获得更好的生成效果
              </button>
              <button className="button">
                下一步
              </button>
              <button 
                className="button" 
                style={{ backgroundColor: 'white', color: '#374151', border: '1px solid #d1d5db' }}
                onClick={() => setSelectedMenuItem('用户中心')}
              >
                <User size={16} style={{ marginRight: '8px' }} />
                用户中心
              </button>
            </div>
          </div>
        </header>

        {/* 主要内容 */}
        <div className="card">
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '32px' }}>
            {/* 左侧表单区域 */}
            <div>
              {selectedMenuItem === '毕业论文' && <TestComponent />}
              {selectedMenuItem === '用户中心' && <UserCenter />}
              {selectedMenuItem === '订单查询' && (
                <div style={{ textAlign: 'center', padding: '48px 0' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: '500', color: '#4b5563', marginBottom: '16px' }}>订单查询功能</h3>
                  <p style={{ color: '#6b7280' }}>请输入您的订单号进行查询</p>
                </div>
              )}
              {selectedMenuItem === '降重/降AI' && (
                <div style={{ textAlign: 'center', padding: '48px 0' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: '500', color: '#4b5563', marginBottom: '16px' }}>降重/降AI功能</h3>
                  <p style={{ color: '#6b7280' }}>上传您的论文进行AI检测和降重处理</p>
                </div>
              )}
              {!['毕业论文', '用户中心', '订单查询', '降重/降AI'].includes(selectedMenuItem) && (
                <div style={{ textAlign: 'center', padding: '48px 0' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: '500', color: '#4b5563', marginBottom: '16px' }}>{selectedMenuItem}</h3>
                  <p style={{ color: '#6b7280' }}>功能正在开发中，敬请期待...</p>
                </div>
              )}
            </div>

            {/* 右侧信息面板 */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* 论文标题 */}
              <div className="card" style={{ padding: '16px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>论文标题</h3>
                <p style={{ fontSize: '14px', color: '#6b7280' }}>设置论文标题与主题</p>
              </div>

              {/* 参考文献 */}
              <div className="card" style={{ padding: '16px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>参考文献</h3>
                <p style={{ fontSize: '14px', color: '#6b7280' }}>添加并管理参考文献</p>
              </div>

              {/* 大纲 */}
              <div className="card" style={{ padding: '16px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>大纲</h3>
                <p style={{ fontSize: '14px', color: '#6b7280' }}>组织论文结构与章节</p>
              </div>

              {/* 下载 */}
              <div className="card" style={{ padding: '16px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>下载</h3>
                <p style={{ fontSize: '14px', color: '#6b7280' }}>导出完整的论文</p>
              </div>

              {/* 说明 */}
              <div className="card" style={{ padding: '16px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px' }}>说明</h3>
                <div style={{ fontSize: '12px', color: '#6b7280', lineHeight: '1.5' }}>
                  <p>1. 输入完整的标题，生成结构更好</p>
                  <p>2. 学历（难度区分）字数（内容篇幅）</p>
                  <p>3. 图表/公式/代码（注意在线好的大纲处右侧点击图表图标进行选择）</p>
                  <p>4. 如果不点击对应章节符号生成对应的图表表等</p>
                </div>
              </div>

              {/* 提示 */}
              <div className="card" style={{ padding: '16px', backgroundColor: '#fef3c7', borderColor: '#f59e0b' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', color: '#92400e' }}>提示</h3>
                <div style={{ fontSize: '12px', color: '#92400e', lineHeight: '1.5' }}>
                  <p>1. 确保标题具体明确，避免过于宽泛</p>
                  <p>2. 确保标题能够准确反映研究内容</p>
                  <p>3. 补充说明内输入，研究思路/方法/内容，参考的数据/案例/资料等</p>
                </div>
              </div>

              {/* 建议 */}
              <div className="card" style={{ padding: '16px', backgroundColor: '#fef7cd', borderColor: '#eab308' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', marginBottom: '8px', color: '#a16207' }}>建议</h3>
                <div style={{ fontSize: '12px', color: '#a16207', lineHeight: '1.5' }}>
                  <p>1. 标题要简洁明确，避免冗长复杂</p>
                  <p>2. 学历选择影响内容深度和复杂度</p>
                  <p>3. 字数选择要符合学校要求</p>
                  <p>4. 建议详细填写补充说明</p>
                  <p>5. 可使用快捷按钮快速填充内容</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* 聊天窗口 */}
      <ChatWindow />
    </div>
  )
}

export default App