import { useState, useEffect } from 'react'
import { 
  User, 
  CreditCard, 
  Gift, 
  Settings, 
  FileText, 
  Clock, 
  TrendingUp,
  Star,
  Zap,
  Crown
} from 'lucide-react'

const API_BASE_URL = 'https://5001-i362990uh7vzwuu0d0o9j-6532622b.e2b.dev'

export function UserCenter() {
  const [userInfo, setUserInfo] = useState(null)
  const [vipPackages, setVipPackages] = useState([])
  const [rechargeAmount, setRechargeAmount] = useState('50')
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    fetchUserInfo()
    fetchVipPackages()
  }, [])

  const fetchUserInfo = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/user/profile`, {
        credentials: 'include'
      })
      const data = await response.json()
      if (data.success) {
        setUserInfo(data.data)
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  const fetchVipPackages = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/user/vip/packages`, {
        credentials: 'include'
      })
      const data = await response.json()
      if (data.success) {
        setVipPackages(data.data)
      }
    } catch (error) {
      console.error('获取VIP套餐失败:', error)
    }
  }

  const handleRecharge = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/user/recharge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          amount: parseFloat(rechargeAmount),
          payment_method: 'alipay'
        })
      })
      const data = await response.json()
      if (data.success) {
        alert('充值成功！')
        fetchUserInfo()
      } else {
        alert('充值失败: ' + data.message)
      }
    } catch (error) {
      console.error('充值失败:', error)
      alert('网络错误，请稍后重试')
    }
  }

  const handleVipPurchase = async (packageType) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/user/vip/purchase`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          package_type: packageType,
          payment_method: 'balance'
        })
      })
      const data = await response.json()
      if (data.success) {
        alert('VIP购买成功！')
        fetchUserInfo()
      } else {
        alert('购买失败: ' + data.message)
      }
    } catch (error) {
      console.error('VIP购买失败:', error)
      alert('网络错误，请稍后重试')
    }
  }

  const renderOverview = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* 用户信息卡片 */}
      <div className="card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            backgroundColor: '#3b82f6',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '24px',
            fontWeight: '600'
          }}>
            {userInfo?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div style={{ flex: 1 }}>
            <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '4px' }}>
              {userInfo?.username || '未登录用户'}
            </h3>
            <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '8px' }}>
              {userInfo?.email || ''}
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              {userInfo?.is_vip ? (
                <span style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  backgroundColor: '#fbbf24',
                  color: 'white',
                  padding: '4px 8px',
                  borderRadius: '12px',
                  fontSize: '12px',
                  fontWeight: '600'
                }}>
                  <Crown size={12} />
                  VIP会员
                </span>
              ) : (
                <span style={{
                  backgroundColor: '#e5e7eb',
                  color: '#6b7280',
                  padding: '4px 8px',
                  borderRadius: '12px',
                  fontSize: '12px'
                }}>
                  普通用户
                </span>
              )}
              <span style={{ fontSize: '12px', color: '#9ca3af' }}>
                注册时间: {userInfo?.created_at ? new Date(userInfo.created_at).toLocaleDateString() : '-'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 统计信息 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        <div className="card" style={{ padding: '20px', textAlign: 'center' }}>
          <CreditCard size={32} style={{ color: '#10b981', margin: '0 auto 12px' }} />
          <h4 style={{ fontSize: '24px', fontWeight: '600', color: '#10b981', marginBottom: '4px' }}>
            ¥{userInfo?.balance?.toFixed(2) || '0.00'}
          </h4>
          <p style={{ color: '#6b7280', fontSize: '14px' }}>账户余额</p>
        </div>

        <div className="card" style={{ padding: '20px', textAlign: 'center' }}>
          <Star size={32} style={{ color: '#f59e0b', margin: '0 auto 12px' }} />
          <h4 style={{ fontSize: '24px', fontWeight: '600', color: '#f59e0b', marginBottom: '4px' }}>
            {userInfo?.points || 0}
          </h4>
          <p style={{ color: '#6b7280', fontSize: '14px' }}>积分</p>
        </div>

        <div className="card" style={{ padding: '20px', textAlign: 'center' }}>
          <FileText size={32} style={{ color: '#3b82f6', margin: '0 auto 12px' }} />
          <h4 style={{ fontSize: '24px', fontWeight: '600', color: '#3b82f6', marginBottom: '4px' }}>
            {userInfo?.total_papers || 0}
          </h4>
          <p style={{ color: '#6b7280', fontSize: '14px' }}>生成论文</p>
        </div>

        <div className="card" style={{ padding: '20px', textAlign: 'center' }}>
          <TrendingUp size={32} style={{ color: '#8b5cf6', margin: '0 auto 12px' }} />
          <h4 style={{ fontSize: '24px', fontWeight: '600', color: '#8b5cf6', marginBottom: '4px' }}>
            {userInfo?.total_words || 0}
          </h4>
          <p style={{ color: '#6b7280', fontSize: '14px' }}>总字数</p>
        </div>
      </div>
    </div>
  )

  const renderRecharge = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <h3 style={{ fontSize: '18px', fontWeight: '600' }}>账户充值</h3>
      
      {/* 当前余额 */}
      <div className="card" style={{ padding: '20px' }}>
        <div style={{ textAlign: 'center' }}>
          <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '8px' }}>当前余额</p>
          <h3 style={{ fontSize: '32px', fontWeight: '600', color: '#10b981' }}>
            ¥{userInfo?.balance?.toFixed(2) || '0.00'}
          </h3>
        </div>
      </div>

      {/* 充值金额选择 */}
      <div className="card" style={{ padding: '20px' }}>
        <h4 style={{ fontSize: '16px', fontWeight: '500', marginBottom: '16px' }}>选择充值金额</h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', gap: '12px', marginBottom: '16px' }}>
          {['50', '100', '200', '500', '1000'].map(amount => (
            <button
              key={amount}
              className="button"
              onClick={() => setRechargeAmount(amount)}
              style={{
                padding: '12px',
                backgroundColor: rechargeAmount === amount ? '#3b82f6' : '#f9fafb',
                color: rechargeAmount === amount ? 'white' : '#374151',
                border: rechargeAmount === amount ? 'none' : '1px solid #e5e7eb'
              }}
            >
              ¥{amount}
            </button>
          ))}
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label className="form-label">自定义金额</label>
          <input
            type="number"
            className="input"
            placeholder="请输入充值金额"
            value={rechargeAmount}
            onChange={(e) => setRechargeAmount(e.target.value)}
            min="1"
            max="10000"
          />
        </div>

        <button 
          className="button"
          onClick={handleRecharge}
          style={{ width: '100%', padding: '12px' }}
        >
          立即充值 ¥{rechargeAmount}
        </button>
      </div>
    </div>
  )

  const renderVip = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <h3 style={{ fontSize: '18px', fontWeight: '600' }}>VIP会员</h3>
      
      {/* VIP状态 */}
      <div className="card" style={{ padding: '20px' }}>
        <div style={{ textAlign: 'center' }}>
          {userInfo?.is_vip ? (
            <div>
              <Crown size={48} style={{ color: '#fbbf24', margin: '0 auto 12px' }} />
              <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#fbbf24', marginBottom: '8px' }}>
                VIP会员
              </h3>
              <p style={{ color: '#6b7280' }}>
                到期时间: {userInfo?.vip_expire_time ? new Date(userInfo.vip_expire_time).toLocaleDateString() : '-'}
              </p>
            </div>
          ) : (
            <div>
              <User size={48} style={{ color: '#6b7280', margin: '0 auto 12px' }} />
              <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#6b7280', marginBottom: '8px' }}>
                普通用户
              </h3>
              <p style={{ color: '#9ca3af' }}>升级VIP享受更多特权</p>
            </div>
          )}
        </div>
      </div>

      {/* VIP套餐 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
        {vipPackages.map((pkg) => (
          <div 
            key={pkg.id} 
            className="card" 
            style={{ 
              padding: '24px', 
              position: 'relative',
              border: pkg.popular ? '2px solid #3b82f6' : '1px solid #e5e7eb'
            }}
          >
            {pkg.popular && (
              <div style={{
                position: 'absolute',
                top: '-10px',
                left: '50%',
                transform: 'translateX(-50%)',
                backgroundColor: '#3b82f6',
                color: 'white',
                padding: '4px 12px',
                borderRadius: '12px',
                fontSize: '12px',
                fontWeight: '600'
              }}>
                推荐
              </div>
            )}

            <div style={{ textAlign: 'center', marginBottom: '20px' }}>
              <h4 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
                {pkg.name}
              </h4>
              <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'center', gap: '4px', marginBottom: '8px' }}>
                <span style={{ fontSize: '32px', fontWeight: '600', color: '#3b82f6' }}>
                  ¥{pkg.current_price}
                </span>
                {pkg.original_price !== pkg.current_price && (
                  <span style={{ fontSize: '16px', color: '#9ca3af', textDecoration: 'line-through' }}>
                    ¥{pkg.original_price}
                  </span>
                )}
              </div>
              <p style={{ color: '#6b7280', fontSize: '14px' }}>
                {pkg.duration}天 · 立省¥{(pkg.original_price - pkg.current_price).toFixed(2)}
              </p>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <h5 style={{ fontSize: '14px', fontWeight: '500', marginBottom: '12px' }}>会员特权</h5>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {pkg.features.map((feature, index) => (
                  <li key={index} style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '8px',
                    marginBottom: '8px',
                    fontSize: '14px',
                    color: '#374151'
                  }}>
                    <Zap size={14} style={{ color: '#10b981' }} />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>

            <button 
              className="button"
              onClick={() => handleVipPurchase(pkg.id)}
              style={{ 
                width: '100%', 
                padding: '12px',
                backgroundColor: pkg.popular ? '#3b82f6' : '#f3f4f6',
                color: pkg.popular ? 'white' : '#374151',
                border: pkg.popular ? 'none' : '1px solid #d1d5db'
              }}
            >
              {userInfo?.is_vip ? '续费' : '立即开通'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )

  const renderSettings = () => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <h3 style={{ fontSize: '18px', fontWeight: '600' }}>账户设置</h3>
      
      <div className="card" style={{ padding: '20px' }}>
        <div style={{ marginBottom: '16px' }}>
          <label className="form-label">用户名</label>
          <input
            type="text"
            className="input"
            value={userInfo?.username || ''}
            disabled
            style={{ backgroundColor: '#f9fafb' }}
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label className="form-label">邮箱</label>
          <input
            type="email"
            className="input"
            value={userInfo?.email || ''}
            placeholder="请输入邮箱地址"
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label className="form-label">真实姓名</label>
          <input
            type="text"
            className="input"
            value={userInfo?.real_name || ''}
            placeholder="请输入真实姓名"
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label className="form-label">手机号码</label>
          <input
            type="tel"
            className="input"
            value={userInfo?.phone || ''}
            placeholder="请输入手机号码"
          />
        </div>

        <button className="button">
          保存设置
        </button>
      </div>
    </div>
  )

  const tabs = [
    { id: 'overview', label: '个人概览', icon: User },
    { id: 'recharge', label: '账户充值', icon: CreditCard },
    { id: 'vip', label: 'VIP会员', icon: Crown },
    { id: 'settings', label: '账户设置', icon: Settings }
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* 标签页导航 */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid #e5e7eb' }}>
        {tabs.map(tab => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 16px',
                border: 'none',
                background: 'none',
                cursor: 'pointer',
                borderBottom: activeTab === tab.id ? '2px solid #3b82f6' : '2px solid transparent',
                color: activeTab === tab.id ? '#3b82f6' : '#6b7280',
                fontWeight: activeTab === tab.id ? '500' : '400'
              }}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* 标签页内容 */}
      {activeTab === 'overview' && renderOverview()}
      {activeTab === 'recharge' && renderRecharge()}
      {activeTab === 'vip' && renderVip()}
      {activeTab === 'settings' && renderSettings()}
    </div>
  )
}