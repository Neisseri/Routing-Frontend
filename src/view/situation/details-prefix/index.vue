<template>
  <div class="details-prefix">
    <!-- 查询区域 -->
    <div class="search-container">
      <el-form :model="formData" inline>
        <el-form-item label="日期">
          <el-select v-model="formData.date" @change="handleDateChange" style="width: 180px">
            <el-option
              v-for="date in availableDates"
              :key="date"
              :label="date"
              :value="date"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="IP前缀">
          <el-input 
            v-model="formData.prefix" 
            placeholder="如: 8.8.8.0/24" 
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="AS号">
          <el-input 
            v-model="formData.asn" 
            placeholder="如: 15169" 
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据展示区域 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="tableData"
        border
        style="width: 100%"
        :height="tableHeight"
      >
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column prop="collector" label="采集器" width="120" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 1 ? 'success' : 'danger'">
              {{ row.type === 1 ? '公告' : '撤回' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="prefix" label="IP前缀" width="150" />
        <el-table-column prop="origin_as" label="源AS" width="100" />
        <el-table-column prop="as_path" label="AS路径">
          <template #default="{ row }">
            {{ row.as_path.join(' → ') }}
          </template>
        </el-table-column>
        <el-table-column prop="next_hop" label="下一跳" width="150" />
        <el-table-column prop="valid" label="有效性" width="100">
          <template #default="{ row }">
            <el-tag :type="row.valid ? 'success' : 'warning'">
              {{ row.valid ? '有效' : '无效' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { searchUpdates } from '@/api/menu1'

// 固定的14天日期选项
const availableDates = [
  '2024-12-01', '2024-12-02', '2024-12-03', '2024-12-04',
  '2024-12-05', '2024-12-06', '2024-12-07', '2024-12-08',
  '2024-12-09', '2024-12-10', '2024-12-11', '2024-12-12',
  '2024-12-13', '2024-12-14'
]

// 表单数据 - 修改默认日期
const formData = reactive({
  date: '2024-12-01', // 默认选择第一天
  prefix: '',
  asn: ''
})

// 分页相关
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const loading = ref(false)
const tableData = ref([])

// 计算表格高度
const tableHeight = window.innerHeight - 300 // 减去其他元素的总高度

// 移除 disabledDate 函数，因为不再需要

// 处理日期变化
const handleDateChange = () => {
  handleSearch()
}

// 搜索数据
const handleSearch = async () => {
  loading.value = true
  try {
    const params = {
      date: formData.date,
      prefix: formData.prefix || undefined,
      asn: formData.asn || undefined,
      page: currentPage.value,
      per_page: pageSize.value
    }
    
    const res = await searchUpdates(params)
    tableData.value = res.data
    total.value = res.total
  } catch (error) {
    ElMessage.error('获取数据失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// 重置查询条件
const handleReset = () => {
  formData.prefix = ''
  formData.asn = ''
  currentPage.value = 1
  handleSearch()
}

// 处理分页大小变化
const handleSizeChange = (val) => {
  pageSize.value = val
  handleSearch()
}

// 处理页码变化
const handleCurrentChange = (val) => {
  currentPage.value = val
  handleSearch()
}

// 初始化加载
handleSearch()
</script>

<style scoped lang="less">
.details-prefix {
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

  .table-container {
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    height: calc(100% - 140px); // 减去搜索区域高度
    display: flex;
    flex-direction: column;
    
    .el-table {
      flex: 1;
    }
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
