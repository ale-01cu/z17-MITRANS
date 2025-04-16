import { Axios } from "../config";
import { API_USER_ME } from "~/config";
import { type User } from "~/types/user";

export default async function getUsersMe(): Promise<User> {
  const res = await Axios.get(API_USER_ME)
  return res.data
}