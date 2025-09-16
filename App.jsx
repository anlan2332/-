import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
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
import logoImage from './assets/logo.jpg'
import { PaperForm } from './components/PaperForm.jsx'
import { ChatWindow } from './components/ChatWindow.jsx'
import './App.css'

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
    { icon: User, label: '商务代理' },
    { icon: Bot, label: '人工排版' }
  ]

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* 左侧导航 */}
      <aside className="w-52 bg-white shadow-sm border-r">
        <div className="p-4">
          {/* Logo */}
          <div className="flex items-center mb-6">
            <img src={logoImage} alt="Logo" className="h-8 w-8 mr-2 rounded" />
            <span className="text-xl font-semibold text-gray-800">百考通</span>
          </div>
          
          {/* 菜单项 */}
          <nav className="space-y-1">
            {menuItems.map((item, index) => {
              const Icon = item.icon
              const isActive = item.label === selectedMenuItem
              return (
                <button
                  key={index}
                  onClick={() => setSelectedMenuItem(item.label)}
                  className={`w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors ${
                    isActive 
                      ? 'bg-blue-50 text-blue-600 border border-blue-200' 
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="h-4 w-4 mr-3" />
                  {item.label}
                </button>
              )
            })}
          </nav>
        </div>
      </aside>

      {/* 主内容区域 */}
      <main className="flex-1 p-6">
        {/* 顶部标题栏 */}
        <header className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-semibold text-gray-800">{selectedMenuItem}</h1>
            <div className="flex space-x-3">
              <Button variant="default" className="bg-blue-600 hover:bg-blue-700">
                输入完整的文章标题，获得更好的生成效果
              </Button>
              <Button variant="default" className="bg-blue-600 hover:bg-blue-700">
                下一步
              </Button>
              <Button variant="outline">
                <User className="h-4 w-4 mr-2" />
                用户中心
              </Button>
            </div>
          </div>
        </header>

        {/* 主要内容 */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* 左侧表单区域 */}
            <div className="lg:col-span-2">
              {selectedMenuItem === '毕业论文' && <PaperForm />}
              {selectedMenuItem === '订单查询' && (
                <div className="text-center py-12">
                  <h3 className="text-lg font-medium text-gray-600 mb-4">订单查询功能</h3>
                  <p className="text-gray-500">请输入您的订单号进行查询</p>
                </div>
              )}
              {selectedMenuItem === '降重/降AI' && (
                <div className="text-center py-12">
                  <h3 className="text-lg font-medium text-gray-600 mb-4">降重/降AI功能</h3>
                  <p className="text-gray-500">上传您的论文进行AI检测和降重处理</p>
                </div>
              )}
              {/* 其他菜单项的内容可以在这里添加 */}
            </div>

            {/* 右侧信息面板 */}
            <div className="space-y-4">
              {/* 论文标题 */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">论文标题</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-sm text-gray-600">设置论文标题与主题</p>
                </CardContent>
              </Card>

              {/* 参考文献 */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">参考文献</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-sm text-gray-600">添加并管理参考文献</p>
                </CardContent>
              </Card>

              {/* 大纲 */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">大纲</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-sm text-gray-600">组织论文结构与章节</p>
                </CardContent>
              </Card>

              {/* 下载 */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">下载</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-sm text-gray-600">导出完整的论文</p>
                </CardContent>
              </Card>

              {/* 说明 */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">说明</CardTitle>
                </CardHeader>
                <CardContent className="pt-0 space-y-2">
                  <div className="text-xs text-gray-600 space-y-1">
                    <p>1. 输入完整的标题，生成结构更好</p>
                    <p>2. 学历（难度区分）字数（内容篇幅）</p>
                    <p>3. 图表/公式/代码（注意在线好的大纲处右侧点击图表图标进行选择）</p>
                    <p>4. 如果不点击对应章节符号生成对应的图表表等</p>
                  </div>
                </CardContent>
              </Card>

              {/* 提示 */}
              <Card className="bg-orange-50 border-orange-200">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-orange-800">提示</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="text-xs text-orange-700 space-y-1">
                    <p>1. 确保标题具体明确，避免过于宽泛</p>
                    <p>2. 确保标题能够准确反映研究内容</p>
                    <p>3. 补充说明内输入，研究思路/方法/内容，参考的数据/案例/资料等</p>
                  </div>
                </CardContent>
              </Card>

              {/* 建议 */}
              <Card className="bg-yellow-50 border-yellow-200">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium text-yellow-800">建议</CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="text-xs text-yellow-700 space-y-1">
                    <p>1. 标题要简洁明确，避免冗长复杂</p>
                    <p>2. 学历选择影响内容深度和复杂度</p>
                    <p>3. 字数选择要符合学校要求</p>
                    <p>4. 建议详细填写补充说明</p>
                    <p>5. 可使用快捷按钮快速填充内容</p>
                  </div>
                </CardContent>
              </Card>
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

