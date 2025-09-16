import { useState, useEffect } from 'react'
import { Search, Eye, Calendar, CreditCard, Package, Clock, CheckCircle, XCircle } from 'lucide-react'

const API_BASE_URL = 'https://5001-i362990uh7vzwuu0d0o9j-6532622b.e2b.dev'

export function OrderQuery() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    checkAuthAndFetchOrders()
  }, [])

  const checkAuthAndFetchOrders = async () => {
    try {
      // 先检查登录状态
      const authResponse = await fetch(`${API_BASE_URL}/api/auth/check-session`, {
        credentials: 'include'
      })
      const authData = await authResponse.json()
      
      if (authData.success) {
        setIsAuthenticated(true)
        fetchOrders()
      } else {
        setIsAuthenticated(false)
      }
    } catch (error) {
      console.error('检查认证状态失败:', error)
      setIsAuthenticated(false)
    }
  }

  const fetchOrders = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/user/orders?status=${statusFilter}`, {
        credentials: 'include'
      })
      const data = await response.json()
      
      if (data.success) {
        setOrders(data.data.orders)
      } else {
        console.error('获取订单失败:', data.message)
      }
    } catch (error) {
      console.error('获取订单失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    fetchOrders()
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle size={16} style={{ color: '#10b981' }} />
      case 'pending':
        return <Clock size={16} style={{ color: '#f59e0b' }} />
      case 'cancelled':
        return <XCircle size={16} style={{ color: '#ef4444' }} />
      default:
        return <Clock size={16} style={{ color: '#6b7280' }} />
    }
  }

  const getStatusText = (status) => {
    const statusMap = {
      'pending': '待处理',
      'processing': '处理中',
      'completed': '已完成',
      'cancelled': '已取消',
      'refunded': '已退款'
    }
    return statusMap[status] || status
  }

  const getProductTypeText = (type) => {
    const typeMap = {
      'balance': '余额充值',
      'vip': 'VIP会员',
      'paper': '论文生成',
      'check': '论文查重',
      'reduce': '降重服务'
    }
    return typeMap[type] || type
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('zh-CN') + ' ' + 
           new Date(dateString).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  if (!isAuthenticated) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <Package size={64} style={{ color: '#9ca3af', margin: '0 auto 16px' }} />
        <h3 style={{ fontSize: '20px', fontWeight: '500', color: '#4b5563', marginBottom: '8px' }}>
          请先登录
        </h3>
        <p style={{ color: '#6b7280', marginBottom: '24px' }}>
          登录后即可查看您的订单信息
        </p>
        <button
          onClick={() => window.location.reload()}
          style={{
            padding: '12px 24px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            cursor: 'pointer'
          }}
        >
          前往登录
        </button>
      </div>
    )
  }

  return (
    <div>
      <h2 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '24px' }}>订单查询</h2>
      
      {/* 搜索和筛选 */}
      <div style={{ 
        display: 'flex', 
        gap: '16px', 
        marginBottom: '24px', 
        flexWrap: 'wrap'
      }}>
        <div style={{ flex: '1', minWidth: '200px' }}>
          <input
            type="text"
            placeholder="搜索订单号或商品名称..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '12px 16px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '14px',
              outline: 'none'
            }}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
        </div>
        
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{
            padding: '12px 16px',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            fontSize: '14px',
            outline: 'none',
            backgroundColor: 'white'
          }}
        >
          <option value="">全部状态</option>
          <option value="pending">待处理</option>
          <option value="processing">处理中</option>
          <option value="completed">已完成</option>
          <option value="cancelled">已取消</option>
        </select>
        
        <button
          onClick={handleSearch}
          disabled={loading}
          style={{
            padding: '12px 20px',
            backgroundColor: loading ? '#9ca3af' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            cursor: loading ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <Search size={16} />
          {loading ? '查询中...' : '查询'}
        </button>
      </div>

      {/* 订单列表 */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ fontSize: '14px', color: '#6b7280' }}>正在加载订单...</div>
        </div>
      ) : orders.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
          <Package size={64} style={{ color: '#9ca3af', margin: '0 auto 16px' }} />
          <h3 style={{ fontSize: '18px', fontWeight: '500', color: '#4b5563', marginBottom: '8px' }}>
            暂无订单
          </h3>
          <p style={{ color: '#6b7280' }}>
            您还没有任何订单记录
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {orders.map((order) => (
            <div
              key={order.id}
              style={{
                border: '1px solid #e5e7eb',
                borderRadius: '12px',
                padding: '20px',
                backgroundColor: 'white'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <span style={{ fontSize: '16px', fontWeight: '600', color: '#1f2937' }}>
                      {order.order_no}
                    </span>
                    {getStatusIcon(order.status)}
                    <span style={{ 
                      fontSize: '14px', 
                      color: order.status === 'completed' ? '#10b981' : 
                             order.status === 'pending' ? '#f59e0b' : '#6b7280'
                    }}>
                      {getStatusText(order.status)}
                    </span>
                  </div>
                  <div style={{ fontSize: '14px', color: '#6b7280' }}>
                    {formatDate(order.created_at)}
                  </div>
                </div>
                
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937' }}>
                    ¥{order.actual_price}
                  </div>
                  {order.original_price > order.actual_price && (
                    <div style={{ fontSize: '12px', color: '#9ca3af', textDecoration: 'line-through' }}>
                      ¥{order.original_price}
                    </div>
                  )}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <Package size={16} style={{ color: '#6b7280' }} />
                <span style={{ fontSize: '14px', color: '#4b5563' }}>
                  {getProductTypeText(order.product_type)} - {order.product_name}
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                <CreditCard size={16} style={{ color: '#6b7280' }} />
                <span style={{ fontSize: '14px', color: '#4b5563' }}>
                  支付方式: {order.payment_method === 'balance' ? '余额支付' : 
                           order.payment_method === 'alipay' ? '支付宝' : 
                           order.payment_method === 'wechat' ? '微信支付' : order.payment_method}
                </span>
                {order.payment_time && (
                  <>
                    <Calendar size={16} style={{ color: '#6b7280' }} />
                    <span style={{ fontSize: '14px', color: '#4b5563' }}>
                      支付时间: {formatDate(order.payment_time)}
                    </span>
                  </>
                )}
              </div>

              {order.transaction_id && (
                <div style={{ 
                  fontSize: '12px', 
                  color: '#6b7280',
                  padding: '8px 12px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '6px',
                  marginTop: '8px'
                }}>
                  交易号: {order.transaction_id}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* 统计信息 */}
      {orders.length > 0 && (
        <div style={{
          marginTop: '24px',
          padding: '16px',
          backgroundColor: '#f9fafb',
          borderRadius: '8px',
          fontSize: '14px',
          color: '#6b7280'
        }}>
          共找到 {orders.length} 个订单
        </div>
      )}
    </div>
  )
}

export default OrderQuery