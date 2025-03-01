import type { Route } from "./+types/protected-route";
import { Outlet, redirect } from "react-router";
import { getCookieFromCookies } from "~/utils/cookies";
import postVerifyApi from "~/api/auth/post-verify-api";

export const loader = async ({ request }: Route.LoaderArgs) => {
  try {
    const cookie = request.headers.get("cookie");
    const token = getCookieFromCookies("access", cookie);
    await postVerifyApi(token)
    
  } catch (error) {
    console.log({error})
    return redirect("/signin");
    
  }
}


export default function ProtectedRoute({}: Route.ComponentProps) {
  return <Outlet />;
}