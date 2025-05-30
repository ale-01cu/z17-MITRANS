import { Axios } from "../config";
import { API_USERS } from "~/config";
import { type User } from "~/types/user";

interface Params {
  email: string
  first_name: string
  is_active: boolean
  is_staff: boolean
  is_superuser: boolean
  last_name: string
  username: string
}

export default async function putUsersApi(data: Params, userId: number | null): Promise<User> {
  if(!userId) throw new Error("PUT USER API ERROR: User id is missing.")
  const res = await Axios.put(API_USERS + userId + "/", data)
  return res.data
}