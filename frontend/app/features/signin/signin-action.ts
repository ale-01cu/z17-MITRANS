import type { Route } from "../../+types/root"
import postSigninApi from "~/api/post-signin-api"
import { setCookie } from "~/utils/cookies"
import { SigninSchema } from "./schemas"
import { getValidationErrors } from "~/utils/errors"
import getUsersMe from "~/api/auth/get-users-me-api"
import { CACHE_KEY, CACHE_TIMESTAMP_KEY } from "~/config"

type ValidationError = {
  type: "validation";
  errors: Record<string, string>; // Un objeto con errores de validación
};

const responseMap: Record<string, string> = {
  "No active account found with the given credentials": "No se encontró una cuenta con los datos ingresados.",
}

export default async function clientAction({ request }: Route.ClientActionArgs) {

  try {
    const formData = await request.formData()
    const data = {
      username: formData.get("username")?.toString() || "",
      password: formData.get("password")?.toString() || ""
    }

    const result = SigninSchema.safeParse(data)
    if(!result.success) {
      throw {
        type: "validation",
        errors: getValidationErrors(result.error.errors)
      } as ValidationError
    }

    const { access, refresh } = await postSigninApi(data)
    setCookie("access", access, 30)
    setCookie("refresh", refresh, 30)

    const userData = await getUsersMe()
    const now = Date.now();

    localStorage.setItem(CACHE_KEY, JSON.stringify(userData));
    localStorage.setItem(CACHE_TIMESTAMP_KEY, now.toString());

    return {ok: true, userData}

  } catch (error: any) {
    if(error.type === "validation") {
      return { ok: false, error: error.errors }
    
    } else if(error.code === "ERR_NETWORK") {
      return { ok: false, error: { request: "No se pudo conectar con el servidor." } }
    
    } else {
      const detail = error?.response?.data?.detail
      if(!detail) return { ok: false, error: { unknown: "No se pudo iniciar sesión." } }
      return { ok: false, error: { request: responseMap[detail] } }

    }

  }
}