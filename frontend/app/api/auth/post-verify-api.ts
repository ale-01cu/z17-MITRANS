import { Axios } from "../config";
import { API_TOKEN_VERIFY } from "~/config";

export default async function postVerifyApi(token: string | null) {
  if(!token) throw new Error("Access token is missing")
  const res = await Axios.post(API_TOKEN_VERIFY, { token });
  return res.data;
}