import axios from 'axios'

axios.defaults.timeout = 3600000
axios.defaults.baseURL = import.meta.env.VITE_GLOB_BASE_URL
// axios.defaults.baseURL = 'https://jsonplaceholder.typicode.com/'

// http request 拦截器
axios.interceptors.request.use(
  (config) => {
    console.log('请求信息：', {
      url: config.url, // 请求的 URL
      method: config.method, // 请求方法（GET、POST 等）
      headers: config.headers, // 请求头
      params: config.params, // 请求的查询参数
      data: config.data // 请求的正文（对于 POST、PUT 等请求）
    });
    return config
  },
  (err) => {
    return Promise.reject(err)
  }
)
// http response 拦截器
axios.interceptors.response.use(
  (response) => {
    return Promise.resolve(response)
  },
  (error) => {
    return Promise.reject(error)
  }
)
// get 方法封装
export function get(url, params = {}) {
  return new Promise((resolve, reject) => {
    axios
      .get(url, { params: params })
      .then((response) => {
        resolve(response.data)
      })
      .catch((err) => {
        reject(err)
      })
  })
}

// post 方法封装
export function post(url, data = {}) {
  return new Promise((resolve, reject) => {
    axios.post(url, { data: data }).then(
      (response) => {
        resolve(response.data)
      },
      (err) => {
        reject(err)
      }
    )
  })
}

// 下载封装
export function exportFile(url, params = {}) {
  return new Promise((resolve, reject) => {
    axios
      .get(url, {
        params: params,
        responseType: 'blob'
      })
      .then((response) => {
        resolve(response)
      })
      .catch((err) => {
        reject(err)
      })
  })
}

// post 附件上传
export function upload(url, data = {}, contentType = 'application/json') {
  return new Promise((resolve, reject) => {
    axios({
      url,
      method: 'post',
      data,
      headers: { 'Content-Type': contentType }
    }).then(
      (response) => {
        resolve(response.data)
      },
      (err) => {
        reject(err)
      }
    )
  })
}
