import { API_SIGNUP } from "~/config";
import { Axios } from "./config";
import type { SignupFormData, SignupResponse } from "~/types/signup";

export default async function postSignupApi(data: SignupFormData): Promise<SignupResponse> {
  const response = await Axios.post(API_SIGNUP, data)
  return response.data
}