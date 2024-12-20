<template>
  <div class="topology-container">
    <div class="search-container">
      <el-form inline>
        <el-form-item label="日期">
          <el-select v-model="selectedDate" @change="handleDateChange" style="width: 180px">
            <el-option
              v-for="date in availableDates"
              :key="date"
              :label="date"
              :value="date"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="content-container">
      <div class="chart-container">
        <div ref="chart" class="chart"></div>
      </div>
      
      <div class="sidebar-container" v-if="selectedNode">
        <h3>{{ selectedNode.country_name }}的AS列表</h3>
        <div class="as-list">
          <div v-for="as in selectedNode.asns" 
               :key="as.asn" 
               class="as-item"
               :class="{ 'expanded': expandedAsns.includes(as.asn) }"
               @click="toggleAsItem(as.asn)">
            <div class="as-header">
              <span class="as-number">AS{{ as.asn }}</span>
              <span class="as-name">{{ as.as_name }}</span>
              <span class="expand-icon">{{ expandedAsns.includes(as.asn) ? '▼' : '▶' }}</span>
            </div>
            <div class="as-content" v-show="expandedAsns.includes(as.asn)">
              <div ref="asChart" class="as-chart"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { getCountryTopology, getAsStats } from '@/api/menu1'
import mockData from '@/mock/topology.json'

const chart = ref(null)
const selectedNode = ref(null)
const expandedAsns = ref([])
const asCharts = new Map()

// 日期选择
const availableDates = [
  '2024-12-01', 
  '2024-12-02', 
  '2024-12-03', 
  '2024-12-04',
  '2024-12-05',
  '2024-12-06',
  '2024-12-07',
  '2024-12-08',
  '2024-12-09',
  '2024-12-10',
  '2024-12-11',
  '2024-12-12',
  '2024-12-13',
  '2024-12-14'
]
const selectedDate = ref('2024-12-01')
let chartInstance = null

onMounted(async () => {
  await fetchTopologyData(selectedDate.value)
})

// 获取拓扑数据的函数
async function fetchTopologyData(date) {
  try {
    // const topologyData = await getCountryTopology({ date })
    const topologyData = mockData // 临时使用模拟数据
    initChart(topologyData)
  } catch (error) {
    console.error('Failed to fetch topology data:', error)
  }
}

// 日期切换处理函数
async function handleDateChange(date) {
  // 清空右侧栏
  selectedNode.value = null
  // 清空展开的AS列表
  expandedAsns.value = []
  // 清理已有的图表实例
  asCharts.forEach(chart => chart.dispose())
  asCharts.clear()
  // 获取新日期的拓扑数据
  await fetchTopologyData(date)
}

function initChart(data) {
  // 如果已存在图表实例，先销毁
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  // 创建新的图表实例
  chartInstance = echarts.init(chart.value)
  const option = {
    title: {
      text: '国家级AS拓扑结构',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: function(params) {
        if (params.dataType === 'node') {
          return `${params.data.country_name}<br/>
                 AS数量: ${params.data.as_count}<br/>
                 前缀数量: ${params.data.total_announced}<br/>
                 有效前缀: ${params.data.total_valid}<br/>
                 有效率: ${(params.data.avg_validity_ratio * 100).toFixed(2)}%`
        } else {
          return `${params.data.source} -> ${params.data.target}<br/>
                 连接数: ${params.data.weight}`
        }
      }
    },
    series: [{
      type: 'graph',
      layout: 'force',
      data: data.nodes.map(node => ({
        ...node,
        name: node.country_code,
        value: node.as_count,
        symbolSize: Math.sqrt(node.as_count) * 3,
        itemStyle: {
          color: `rgba(${Math.random() * 255},${Math.random() * 255},${Math.random() * 255},0.8)`
        }
      })),
      links: data.links.map(link => ({
        ...link,
        lineStyle: {
          width: Math.log(link.weight),
          opacity: 0.7
        }
      })),
      roam: true,
      nodeScaleRatio: 0, // 节点不随缩放变化大小
      label: {
        show: true,
        position: 'right',
        formatter: '{b}'
      },
      force: {
        repulsion: 350,
        gravity: 0.1,
        edgeLength: [50, 200],
        layoutAnimation: true
      },
      emphasis: {
        focus: 'adjacency'
      }
    }]
  }
  
  chartInstance.setOption(option)
  
  // 监听节点点击事件
  chartInstance.on('click', params => {
    if (params.dataType === 'node') {
      selectedNode.value = params.data
    }
  })

  // 监听空白处点击事件，取消选中
  chartInstance.getZr().on('click', params => {
    if (!params.target) {
      selectedNode.value = null
    }
  })
  
  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chartInstance && chartInstance.resize()
  })
}

async function toggleAsItem(asn) {
  const index = expandedAsns.value.indexOf(asn)
  if (index === -1) {
    // 展开
    expandedAsns.value.push(asn)
    // 获取AS统计数据
    try {
      const stats = await getAsStats(asn)
      // 等待DOM更新
      await nextTick()
      initAsChart(asn, stats)
    } catch (error) {
      console.error(`Failed to fetch stats for AS${asn}:`, error)
    }
  } else {
    // 折叠
    expandedAsns.value.splice(index, 1)
    // 销毁图表实例
    if (asCharts.has(asn)) {
      asCharts.get(asn).dispose()
      asCharts.delete(asn)
    }
  }
}

function initAsChart(asn, stats) {
  const container = document.querySelector(`[data-asn="${asn}"] .as-chart`)
  if (!container) return

  const chart = echarts.init(container)
  asCharts.set(asn, chart)

  const option = {
    grid: {
      top: 20,
      right: 20,
      bottom: 20,
      left: 50
    },
    xAxis: {
      type: 'category',
      data: stats.map(item => item.date)
    },
    yAxis: {
      type: 'value',
      name: '前缀数量'
    },
    tooltip: {
      trigger: 'axis'
    },
    series: [
      {
        name: '已公告前缀',
        type: 'line',
        data: stats.map(item => item.announced_prefixes),
        smooth: true
      },
      {
        name: '有效前缀',
        type: 'line',
        data: stats.map(item => item.valid_announcements),
        smooth: true
      }
    ]
  }
  chart.setOption(option)
}

// 组件卸载时清理所有图表实例
onUnmounted(() => {
  asCharts.forEach(chart => chart.dispose())
  asCharts.clear()
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped lang="less">
.topology-container {
  padding: 20px;
  height: calc(100vh - 84px);
  background-color: #f5f7fa;
  overflow: hidden;

  .search-container {
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }

  .content-container {
    display: flex;
    gap: 20px;
    height: calc(100% - 100px); // 减去搜索区域高度
    width: 100%;
    position: relative; // 添加相对定位

    .chart-container {
      width: calc(100% - 370px); // 固定宽度，考虑右侧栏宽度(350px)和间距(20px)
      flex: none; // 移除弹性布局
      background-color: #fff;
      padding: 20px;
      border-radius: 4px;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      height: 100%;
      overflow: hidden;

      .chart {
        height: 100%;
        width: 100%;
      }
    }

    .sidebar-container {
      width: 350px; // 改回固定宽度
      position: absolute; // 使用绝对定位
      right: 0; // 固定在右侧
      top: 0;
      bottom: 0;
      min-width: 350px; // 设置最小宽度
      max-width: 450px; // 设置最大宽度
      background-color: #fff;
      padding: 20px;
      border-radius: 4px;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      overflow-y: auto;

      .as-list {
        max-height: calc(100vh - 250px);
        overflow-y: auto;
      }

      h3 {
        margin-top: 0;
        margin-bottom: 20px;
        color: #303133;
      }
    }
  }

  // 保留原有的 AS 列表相关样式
  .as-list {
    margin-top: 10px;
  }

  .as-item {
    padding: 8px;
    border-bottom: 1px solid #eee;
    display: flex;
    align-items: center;
  }

  .as-number {
    font-weight: bold;
    margin-right: 10px;
    color: #409EFF;
  }

  .as-name {
    color: #606266;
    font-size: 14px;
  }

  .as-header {
    display: flex;
    align-items: center;
    cursor: pointer;
  }

  .expand-icon {
    margin-left: auto;
    font-size: 12px;
    color: #909399;
  }

  .as-content {
    margin-top: 10px;
    padding: 10px;
    background: #f5f7fa;
    border-radius: 4px;
  }

  .as-chart {
    height: 200px;
    width: 100%;
  }

  .as-item.expanded {
    padding: 12px 8px;
    background: #fff;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .date-selector {
    padding: 20px 0;
    text-align: center;
  }
}
</style>