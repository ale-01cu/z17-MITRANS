import { Axios } from "./config"
import { API_SIGNIN } from "~/config"
import type { SigninFormData } from "~/types/signin"

export default async function postSigninApi(data: SigninFormData): Promise<any> {
  const response = await Axios.post(API_SIGNIN, data)
  return response.data
}