import type { Route } from "../../+types/root"
import postSignupApi from "~/api/post-signup-api"
import type { SignupFormData } from "~/types/signup"

export default async function clientAction({ request }: Route.ClientActionArgs) {
  try {
    const formData = await request.formData()
    const data = {
      username: formData.get("username"),
      email: formData.get("email"),
      first_name: formData.get("first_name"),
      last_name: formData.get("last_name"),
      password: formData.get("password"),
      re_password: formData.get("re_password")
    }
  
    await postSignupApi(data)
    return {ok: true}

  } catch (error) {
    console.error(error)
    return { error: "Error al registrar." }

  }
}