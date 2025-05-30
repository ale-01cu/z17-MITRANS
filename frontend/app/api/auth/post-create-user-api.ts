import { Axios } from "../config";
import { API_USERS } from "~/config";
import { type User } from "~/types/user";
import { type SignupFormData } from "~/types/signup";


export default async function postCreateUsersApi(data: SignupFormData): Promise<User> {
  const res = await Axios.post(API_USERS, data)
  return res.data
}