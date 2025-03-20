import axios from "axios"
import { SERVER_BASE_URL } from "~/config"
import { getCookie } from "~/utils/cookies"

export const CONFIG = {
  baseURL: SERVER_BASE_URL,
  headers: {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": ""
  },
}

const createInstance = () => {
  const token = getCookie("access")
  if(token) CONFIG.headers.Authorization = `Bearer ${token}`
  return axios.create(CONFIG)
}

export const Axios = createInstance()