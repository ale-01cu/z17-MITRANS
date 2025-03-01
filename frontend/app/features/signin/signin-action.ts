import type { Route } from "../../+types/root"
import postSigninApi from "~/api/post-signin-api"
import { setCookie } from "~/utils/cookies"
import { SigninSchema } from "./schemas"
import { getValidationErrors } from "~/utils/errors"

type ValidationError = {
  type: "validation";
  errors: Record<string, string>; // Un objeto con errores de validación
};

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

    console.log("iniciando sesion...")
    console.log({data})
  
    const { access, refresh } = await postSigninApi(data)
    setCookie("access", access, 30)
    setCookie("refresh", refresh, 30)
    return {ok: true}

  } catch (error: any) {
    if(error.type === "validation") {
      return { ok: false, error: error.errors }
    }
    return { ok: false, error: { unknown: "Error desconocido." } }

  }
}