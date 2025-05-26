// 环境配置
const ENV = {
    development: { 
        apiBaseUrl: 'http://localhost:8000'
    },
    production: {
        apiBaseUrl: 'https://ai.dl-dd.com'
    }
}

// 当前环境
const currentEnv = process.env.NODE_ENV || 'production'

// 导出配置
export default { 
    //apiBaseUrl: ENV[currentEnv].apiBaseUrl
    apiBaseUrl:'http://localhost:8000', 
    //apiBaseUrl: 'https://ai.dl-dd.com'
} 