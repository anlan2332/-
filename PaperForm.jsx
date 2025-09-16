import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Upload, Lightbulb, FileText, Download, Loader2, Sparkles } from 'lucide-react'
import apiService from '../services/api.js'

export function PaperForm() {
  const [formData, setFormData] = useState({
    articleTitle: '',
    education: '专科',
    wordCount: '',
    language: 'chinese',
    chartType: 'chartCode',
    description: '',
    uploadedFile: null
  })

  const [generatedOutline, setGeneratedOutline] = useState(null)
  const [generatedTitles, setGeneratedTitles] = useState([])
  const [showTitles, setShowTitles] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isGeneratingTitles, setIsGeneratingTitles] = useState(false)

  const quickButtons = [
    '控写论文', '摘要', '创新点', '参考文献', '研究方法', 
    '开题报告内容模板', '创新背景意义'
  ]

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleQuickButtonClick = (buttonText) => {
    const suggestions = {
      '控写论文': '开始撰写完整的论文内容，包括各个章节的详细阐述。',
      '摘要': '论文摘要应简明扼要地概括研究目的、方法、结果和结论。',
      '创新点': '请明确您研究的创新之处，包括理论创新、方法创新或应用创新。',
      '参考文献': '建议使用权威的学术期刊、专著和会议论文作为参考文献。',
      '研究方法': '选择适合您研究问题的研究方法，如定量研究、定性研究或混合研究。',
      '开题报告内容模板': '开题报告应包括：研究背景、研究意义、文献综述、研究方法、预期成果等。',
      '创新背景意义': '阐述您的研究在当前学术背景下的重要性和实际应用价值。'
    }
    
    setFormData(prev => ({
      ...prev,
      description: prev.description + (prev.description ? '\n\n' : '') + suggestions[buttonText]
    }))
  }

  const handleGenerateTitles = async () => {
    if (!formData.articleTitle.trim()) {
      alert('请先输入关键词或主题')
      return
    }

    setIsGeneratingTitles(true)
    try {
      const response = await apiService.generateTitle({
        keywords: formData.articleTitle,
        education: formData.education,
        field: '计算机科学' // 可以根据需要调整
      })
      
      if (response.success) {
        setGeneratedTitles(response.titles)
        setShowTitles(true)
      } else {
        alert('生成标题失败: ' + response.message)
      }
    } catch (error) {
      console.error('生成标题失败:', error)
      alert('生成标题失败，请检查网络连接或后端服务')
    } finally {
      setIsGeneratingTitles(false)
    }
  }

  const handleSelectTitle = (title) => {
    setFormData(prev => ({ ...prev, articleTitle: title }))
    setShowTitles(false)
  }

  const generateOutline = async () => {
    if (!formData.articleTitle.trim()) {
      alert('请先输入文章标题')
      return
    }

    setIsGenerating(true)
    
    try {
      const response = await apiService.generateOutline({
        title: formData.articleTitle,
        education: formData.education,
        word_count: formData.wordCount || '8000',
        description: formData.description
      })
      
      if (response.success) {
        setGeneratedOutline(response.outline)
      } else {
        alert('生成大纲失败: ' + response.message)
      }
    } catch (error) {
      console.error('生成大纲失败:', error)
      alert('生成大纲失败，请检查网络连接或后端服务')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleFileUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      setFormData(prev => ({
        ...prev,
        uploadedFile: file
      }))
    }
  }

  return (
    <div className="space-y-6">
      {/* 文章标题 */}
      <div className="space-y-2">
        <Label htmlFor="title" className="text-sm font-medium text-gray-700">
          文章标题 <span className="text-red-500">*</span>
        </Label>
        <div className="flex space-x-2">
          <Input
            id="title"
            placeholder="请输入标题或关键词"
            value={formData.articleTitle}
            onChange={(e) => handleInputChange('articleTitle', e.target.value)}
            className="flex-1"
          />
          <Button 
            onClick={handleGenerateTitles}
            disabled={isGeneratingTitles}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {isGeneratingTitles ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <Sparkles className="h-4 w-4 mr-2" />
            )}
            智能选题
          </Button>
        </div>
        
        {/* 显示生成的标题选项 */}
        {showTitles && generatedTitles.length > 0 && (
          <Card className="bg-blue-50 border-blue-200">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-blue-800">AI推荐标题</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {generatedTitles.map((title, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  className="w-full justify-start text-left h-auto p-2 text-sm hover:bg-blue-100"
                  onClick={() => handleSelectTitle(title)}
                >
                  {index + 1}. {title}
                </Button>
              ))}
            </CardContent>
          </Card>
        )}
      </div>

      {/* 学历和字数 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label className="text-sm font-medium text-gray-700">
            学历 <span className="text-red-500">*</span>
          </Label>
          <Select value={formData.education} onValueChange={(value) => handleInputChange('education', value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="专科">专科</SelectItem>
              <SelectItem value="本科">本科</SelectItem>
              <SelectItem value="硕士">硕士</SelectItem>
              <SelectItem value="博士">博士</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label className="text-sm font-medium text-gray-700">论文字数:</Label>
          <Select value={formData.wordCount} onValueChange={(value) => handleInputChange('wordCount', value)}>
            <SelectTrigger>
              <SelectValue placeholder="请选择字数" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="3000">3000字</SelectItem>
              <SelectItem value="5000">5000字</SelectItem>
              <SelectItem value="8000">8000字</SelectItem>
              <SelectItem value="10000">10000字</SelectItem>
              <SelectItem value="15000">15000字</SelectItem>
              <SelectItem value="20000">20000字</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* 语言选择 */}
      <div className="space-y-2">
        <Label className="text-sm font-medium text-gray-700">语言:</Label>
        <RadioGroup value={formData.language} onValueChange={(value) => handleInputChange('language', value)}>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="chinese" id="chinese" />
            <Label htmlFor="chinese">中文</Label>
          </div>
        </RadioGroup>
      </div>

      {/* 图表公式 */}
      <div className="space-y-2">
        <Label className="text-sm font-medium text-gray-700">图表公式:</Label>
        <RadioGroup value={formData.chartType} onValueChange={(value) => handleInputChange('chartType', value)}>
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="chartCode" id="chartCode" />
            <Label htmlFor="chartCode">图表/公式/代码</Label>
          </div>
        </RadioGroup>
      </div>

      {/* 上传开题报告 */}
      <div className="space-y-2">
        <Label className="text-sm font-medium text-gray-700">上传开题报告:</Label>
        <div className="flex items-center space-x-2">
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".pdf,.doc,.docx"
            onChange={handleFileUpload}
          />
          <Button 
            variant="default" 
            className="bg-blue-600 hover:bg-blue-700"
            onClick={() => document.getElementById('file-upload').click()}
          >
            <Upload className="h-4 w-4 mr-2" />
            上传开题报告
          </Button>
          {formData.uploadedFile && (
            <span className="text-sm text-gray-600">
              已上传: {formData.uploadedFile.name}
            </span>
          )}
        </div>
      </div>

      {/* 补充说明 */}
      <div className="space-y-2">
        <Label className="text-sm font-medium text-gray-700">补充说明:</Label>
        <Textarea
          placeholder="请详细描述您的研究内容、方法、数据来源等..."
          value={formData.description}
          onChange={(e) => handleInputChange('description', e.target.value)}
          className="min-h-[120px] border-0 bg-gray-50"
        />
      </div>

      {/* 快捷按钮 */}
      <div className="space-y-2">
        <Label className="text-sm font-medium text-gray-700">快捷操作:</Label>
        <div className="flex flex-wrap gap-2">
          {quickButtons.map((button, index) => (
            <Button
              key={index}
              variant="outline"
              size="sm"
              className="text-xs"
              onClick={() => handleQuickButtonClick(button)}
            >
              {button}
            </Button>
          ))}
        </div>
      </div>

      {/* 生成大纲按钮 */}
      <div className="flex space-x-2">
        <Button 
          onClick={generateOutline}
          disabled={isGenerating}
          className="bg-green-600 hover:bg-green-700"
        >
          {isGenerating ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              生成中...
            </>
          ) : (
            <>
              <FileText className="h-4 w-4 mr-2" />
              生成大纲
            </>
          )}
        </Button>
        
        {generatedOutline && (
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            导出大纲
          </Button>
        )}
      </div>

      {/* 生成的大纲 */}
      {generatedOutline && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg text-green-600">生成的论文大纲</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center">
                <h3 className="font-semibold text-lg mb-2">{generatedOutline.title}</h3>
                <div className="text-sm text-gray-600">
                  总字数: {generatedOutline.total_word_count} | 生成时间: {generatedOutline.generated_at}
                </div>
              </div>
              
              <div className="space-y-4">
                {generatedOutline.chapters.map((chapter) => (
                  <div key={chapter.id} className="border-l-4 border-blue-500 pl-4">
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="font-medium text-blue-700">{chapter.title}</h4>
                      <span className="text-sm text-gray-500">约{chapter.word_count}字</span>
                    </div>
                    <ul className="space-y-1">
                      {chapter.subsections.map((subsection, index) => (
                        <li key={index} className="text-sm text-gray-600 ml-4 list-disc">
                          {subsection}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 字数统计 */}
      <div className="text-right text-sm text-gray-500">
        {formData.description.length}/1500
      </div>
    </div>
  )
}

