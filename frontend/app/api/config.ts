import axios from "axios"
import { SERVER_BASE_URL } from "~/config"

export const CONFIG = {
  baseURL: SERVER_BASE_URL,
  headers: {
    "Accept": "application/json",
    "Content-Type": "application/json",
  },
}

export const Axios = axios.create(CONFIG)