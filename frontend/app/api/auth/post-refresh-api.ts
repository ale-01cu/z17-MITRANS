import { Axios } from "../config";
import { API_TOKEN_REFRESH } from "~/config";

export default async function postRefreshApi(token: string) {
  const res = await Axios.post(API_TOKEN_REFRESH, { token });
  return res.data;
}