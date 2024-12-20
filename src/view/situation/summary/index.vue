<template>
  <div class="container">
    <MyMap :dataSource="dataSource" v-if="isShow"/>
  </div>
</template>


<script setup>
import MyMap from '@/components/MyMap/index.vue'
// import { dataSource } from './js/static-var'
import { summary } from '@/api/menu1'
import { ref, onMounted } from 'vue'
import { shapeData } from '@/components/MyMap/mapBuilder'
// Request data from the server
const dataSource = ref([
        { "cc": "CN", "times": 0 },
        { "cc": "IN", "times": 0.1 },
        { "cc": "ID", "times": 0.3 },
        { "cc": "BR", "times": 0.7 },
        { "cc": "US", "times": 0.9 },
      ])
const isShow=ref(true);

summary().then(res => {
  console.log('res', res)
  // parse the res data
  /*
  {
            'nodes': [
                {
                    'country_code': str,
                    'country_name': str,
                    'lat': float,
                    'lon': float,
                    'as_count': int,
                    'total_announced': int,
                    'total_valid': int,
                    'avg_validity_ratio': float,
                    'asns': [
                        {
                            'asn': int,
                            'as_name': str
                        }
                    ]
                }
            ],
            'links': [
                {
                    'source': str(country_code),
                    'target': str(country_code),
                    'weight': int
                }
            ]
        }
  */
  const nodes = res['nodes']
  const links = res['links']
  
  // 清空原有数据
  dataSource.value.length = 0
  
  // 使用响应式方法更新数组
  const newData = nodes.map(node => ({
    cc: node['country_code'],
    times: node['avg_validity_ratio']
  }))
  dataSource.value.push(...newData)
  
  for (let data of dataSource.value) {
    console.log('cc = ', data.cc, 'times = ', data.times)
  }
  isShow.value = true
}).catch(err => {
    console.log(err)
})
</script>

<style scoped lang="less">
.container{
  height: calc(100vh - 142px);
  .map{
    height: 100%;
  }
}
</style>
