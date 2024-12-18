<template>
  <div class="topology">
    <Table
      :table-head="tableHead"
      :table-data="tableData"
      :operation="['del']"
      :total="8000"
      :list-loading="listLoading"
      style="height:calc(100vh - 250px);"
      @handleDelete="handleDelete"
      @paginationChange="paginationChange"
    />
    <MyMap 
      :dataSource="dataSrcFromFile"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { formItem, tableHead } from './js/static-var'
import { ElMessage, ElMessageBox } from 'element-plus'
import Table from '@/components/Table/index.vue'
import MyMap from '@/components/MyMap/index.vue'
import { dataSource } from '../summary/js/static-var'

const formData = reactive({ name: '', age: '', classes: '' })
const listLoading = ref(true)
const tableData = reactive([])
const dataSrcFromFile = ref([])

onMounted(async () => {
  dataSrcFromFile.value = [
        { "cc": "CN", "times": 10 },
        { "cc": "IN", "times": 8 },
        { "cc": "ID", "times": 7 },
        { "cc": "BR", "times": 6 },
        { "cc": "US", "times": 10 },
  ]
  try {
    // 异步读取 JSON 文件
    const response = await fetch('/country_topology.json');
    if (!response.ok) {
      throw new Error(`Failed to load JSON: ${response.statusText}`);
    }
    const data_json = await response.json();

    // 将数据映射为所需的 dataSrcFromFile
    dataSrcFromFile.value = data_json["nodes"].map((item) => ({
      cc: item.country_code,
      times: item.as_count
    }));

    console.log('dataSrcFromFile', dataSrcFromFile); // 打印输出 dataSource
  } catch (error) {
    console.error('Error loading JSON:', error);
  }
});

setTimeout(() => {
  for (let i = 0; i < 20; i++) {
    tableData.push({
      index: i + 1,
      name: `wcy${i + 1}`,
      userName: 'admin',
      role: '管理员',
      sex: '男',
      idNo: '411503199903041234',
      phone: '18186421234',
      email: '354065853@qq.com',
      createTime: '2022-5-31 09:30:00',
      creatorName: 'admin'
    })
  }
  listLoading.value = false
}, 200)

function handleDelete(row) {
  console.log('删除', row)
  ElMessageBox({
    title: '提示',
    message: '确定要删除吗?',
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    callback: (action) => {
      if (action === 'confirm') {
        ElMessage.success('删除成功')
      }
    }
  })
}
function getList(val) {
  console.log('查询数据', val)
}
function clearForm() {
  console.log('清除数据')
}
function paginationChange(data) {
  console.log('页码变化', data)
}

</script>
<style scoped lang="less">
.topology{
  .btn-list{
    margin-bottom: 10px;
    display: flex;
    flex-direction: row-reverse;
  }
}
</style>

<!-- TODO: Implement the template and scripts to show the topology of ASes -->
<!-- You need to think about how to do this! -->