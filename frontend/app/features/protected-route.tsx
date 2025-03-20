import type { Route } from "./+types/protected-route";
import { Outlet, redirect } from "react-router";
import { getCookieFromCookies, getCookie } from "~/utils/cookies";
import postVerifyApi from "~/api/auth/post-verify-api";

export const clientLoader = async ({ request }: Route.ClientLoaderArgs) => {
  try {
    const token = getCookie("access");
    await postVerifyApi(token);
    return true
    
  } catch (error) {
    console.log(error)
    return redirect("/signin");
    
  }
}


export default function ProtectedRoute({ loaderData }: Route.ComponentProps) { 
  if(!loaderData) return null
  return <Outlet />;
}