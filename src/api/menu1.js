import { get, post } from '@/utils/axios.js'

// 1. AS拓扑结构接口
export const getCountryTopology = (params) => get('/topology/country', params)
export const getAsStats = (asn, params) => get(`/topology/as/${asn}`, params)

// 2. BGP更新查询接口
export const getPrefixTrend = (params) => get('/updates/trend', params)
export const searchUpdates = (params) => get('/updates/search', params)

// 3. 数据下载接口
export const downloadData = (params) => get('/download/data', params)

// 4. WebSocket连接封装
export const initWebSocket = (socket) => {

  // 监听连接响应事件
  socket.on('connection_response', (data) => {
    console.log('Connected to server:', data)
  })

  // BGP 更新事件监听
  socket.on('bgp_update', (data) => {
    console.log('Received BGP update:', data)
    // 在这里处理接收到的 BGP 更新数据
  })

  // 捕获开始事件监听
  socket.on('capture_started', (data) => {
    console.log('Capture started:', data)
  })

  // 捕获停止事件监听
  socket.on('capture_stopped', (data) => {
    console.log('Capture stopped:', data)
  })

  // 捕获错误事件监听
  socket.on('capture_error', (data) => {
    console.error('Capture error:', data)
  })

  // 捕获状态事件监听
  socket.on('capture_status', (data) => {
    console.log('Capture status:', data)
  })

  return {
    // 开始捕获
    startCapture: () => {
      socket.emit('start_capture')
    },
    // 停止捕获
    stopCapture: () => {
      socket.emit('stop_capture')
    },
    // 获取状态
    getStatus: () => {
      socket.emit('get_status')
    },
    // 断开连接
    disconnect: () => {
      socket.disconnect()
    }
  }
}

// 使用示例：
/*
import { io } from 'socket.io-client'
import { initWebSocket, getCountryTopology } from '@/api/menu1'

// 1. REST API调用
const fetchTopology = async () => {
  try {
    const data = await getCountryTopology({ date: '2024-12-01' })
    // 处理拓扑数据
  } catch (error) {
    console.error('Failed to fetch topology:', error)
  }
}

// 2. WebSocket连接
const socket = io('http://localhost:5000/bgp')
const bgpSocket = initWebSocket(socket)

// 开始实时捕获
bgpSocket.startCapture({
  asn: 15169,
  prefix: '8.8.8.0/24'
})

// 停止捕获
bgpSocket.stopCapture()

// 组件卸载时断开连接
onUnmounted(() => {
  bgpSocket.disconnect()
})
*/