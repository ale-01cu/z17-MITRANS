import { Input } from "~/components/ui/input"
import { Button } from "~/components/ui/button"
import { Link } from "react-router"
import { useForm } from "react-hook-form"
import { useEffect, useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { SigninSchema } from "./schemas"
import { EyeOffIcon, EyeIcon, Loader2 } from "lucide-react"
import { useFetcher } from "react-router"
import { useNavigate } from "react-router"
import ErrorMessage from "~/components/error-message"
import type { SigninFormData } from "~/types/signin"

interface ErrorsResponse {
  request?: string,
  username?: string,
  password?: string
} 

export default function SigninForm() {
  const [showPassword, setShowPassword] = useState(false)
  const { register, handleSubmit, formState: { errors } } = useForm({ 
    resolver: zodResolver(SigninSchema) })
  const fetcher = useFetcher()
  const isLoading = fetcher.state == "submitting"
  const navegate = useNavigate()
  const [ resErrors, setResErrors ] = useState<ErrorsResponse>({})

  useEffect(() => {
    if(!fetcher.data) return

    if(fetcher.data?.ok === false) 
      setResErrors(fetcher.data.error)
    else navegate("/")

  }, [fetcher.data])

  const onSubmit = (data: SigninFormData) => {
    fetcher.submit(data, {
      method: "post",
      action: "/signin",
    });
  };


  return (
    <fetcher.Form
      method="post"
      action="/signin"
      onSubmit={handleSubmit(onSubmit)} 
    >
      <div className="flex flex-col gap-8 w-96">
        <div className="space-y-2">
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
            Nombre de usuario
          </label>
          <Input
            placeholder="Escriba su nombre de usuario"
            type="text"
            {...register('username')}
          />
          {errors?.username?.message && ( 
            <ErrorMessage message={errors.username.message} />
          )}
        </div>
        <div className="space-y-2">
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            Contraseña
          </label>

          <div className="relative">
            <Input
              placeholder="Escriba su contraseña"
              type={showPassword ? "text" : "password"}
              {...register('password')}
            />
            <Button
              variant="ghost"
              className="cursor-pointer absolute right-0 top-1/2 transform -translate-y-1/2"
              type="button"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <EyeIcon className="w-5 h-5" />
              ) : (
                <EyeOffIcon className="w-5 h-5" />
              )}
            </Button>
          </div>
          {errors?.password?.message && (
            <ErrorMessage message={errors.password.message} />
          )}
        </div>

        <Link to="/signup" className="text-sm text-center">
          ¿No tienes una cuenta?
        </Link>

        <Button type="submit">
          {isLoading && <Loader2 className="animate-spin" />}
          Acceder
        </Button>

        {resErrors?.request && 
          <ErrorMessage message={resErrors?.request} />
        }  
      </div>

    </fetcher.Form>
  )
}