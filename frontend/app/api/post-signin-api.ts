import { Axios } from "./config"
import { API_SIGNIN } from "~/config"


export default async function postSigninApi(data: any) {
  const response = await Axios.post(API_SIGNIN, data)
  return response.data
}