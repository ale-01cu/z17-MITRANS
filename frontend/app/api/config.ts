import axios from "axios"
import { SERVER_BASE_URL } from "~/config"
import { getCookie } from "~/utils/cookies"

export const CONFIG = {
  baseURL: SERVER_BASE_URL,
  headers: {
    "Accept": "application/json",
    "Content-Type": "application/json"
    // Don't set Authorization here
  },
}

const Axios = axios.create(CONFIG)

// Add a request interceptor to always get the latest token
Axios.interceptors.request.use(
  (config) => {
    const token = getCookie("access")
    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    } else if (config.headers) {
      delete config.headers.Authorization
    }
    return config
  },
  (error) => Promise.reject(error)
)

export { Axios }