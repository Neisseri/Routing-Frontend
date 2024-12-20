<template>
  <div class="summary">
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
    <div class="map-container">
      <MyMap :dataSource="mapData" v-if="isShow"/>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import MyMap from '@/components/MyMap/index.vue'
import { getCountryTopology } from '@/api/menu1'
import { shapeData } from '@/components/MyMap/mapBuilder'
// import mockData from '@/mock/topology.json'

const mapData = ref([])
const isShow = ref(false)

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

// 获取数据并处理
async function fetchTopologyData(date) {
  try {
    const data = await getCountryTopology({ date })
    // const data = mockData // 临时使用模拟数据
    // 将topology数据转换为地图所需格式
    mapData.value = data.nodes.map(node => ({
      cc: node.country_code,
      name: node.country_name,
      times: node.avg_validity_ratio // 使用有效性比例作为颜色值
    }))
    
    isShow.value = true
  } catch (error) {
    console.error('Failed to fetch topology data:', error)
  }
}

// 日期切换处理函数
async function handleDateChange(date) {
  isShow.value = false
  await fetchTopologyData(date)
}

onMounted(async () => {
  await fetchTopologyData(selectedDate.value)
})
</script>

<style scoped lang="less">
.summary {
  padding: 20px;
  height: calc(100vh - 84px); // 减去顶部导航栏高度
  background-color: #f5f7fa;
  overflow: hidden; // 防止内容溢出

  .search-container {
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }

  .map-container {
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    height: calc(100vh - 200px); // 调整高度
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    overflow: hidden; // 防止地图溢出
  }
}
</style>
