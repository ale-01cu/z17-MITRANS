import { Input } from "~/components/ui/input"
import { Button } from "~/components/ui/button"
import { Link } from "react-router"
import { EyeOffIcon, EyeIcon } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { SignupSchema } from "./schemas"
import postSignupApi from "~/api/post-signup-api"
import type { SignupFormData } from "~/types/signup"
import { Loader2, AlertCircleIcon, CheckCircleIcon} from "lucide-react"
import { toast } from "sonner"
import SignupDialog from "./signup-dialog"

export default function SignupForm() {
  const [showPassword, setShowPassword] = useState(false)
  const [showRePassword, setShowRePassword] = useState(false)
  const { register, handleSubmit, setValue, formState: { errors } } = useForm({ 
    resolver: zodResolver(SignupSchema) })
  const [ isLoading, setIsLoading ] = useState(false)
  const [ isSuccess, setIsSuccess ] = useState(false)

  const myHandleSubmit = async (data: SignupFormData) => {
    try {
      setIsLoading(true)
      await postSignupApi(data)
      toast("Registro exitoso.", {
        icon: <CheckCircleIcon className="w-4 h-4" />,
        style: { backgroundColor: "green" },
        closeButton: true
      })
      setIsSuccess(true)
      setValue('username', '');
      setValue('email', '');
      setValue('first_name', '');
      setValue('last_name', '');
      setValue('password', '');
      setValue('re_password', '');

    } catch (error) {
      console.error(error)
      toast("Error al registrar.", {
        icon: <AlertCircleIcon className="w-4 h-4" />,
        description: "No se ha podido realizar el registro debido a un error.",
        style: { backgroundColor: "red" },
        closeButton: true,
        cancelButtonStyle: { background: "white" }
      })
      
    } finally { setIsLoading(false) }
  }

  const DialogHandleChange = (open: boolean) => {
    setIsSuccess(open)
  }

  return (
    <form
      method="post"
      // action="/signup"
      onSubmit={handleSubmit(myHandleSubmit)}
    >
      <SignupDialog 
        isOpen={isSuccess} 
        onOpenChange={DialogHandleChange}
      />
      <div className="flex flex-col gap-6 w-96">
        {/* Campo de Nombre de Usuario */}
        <div className="space-y-2">
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
            Nombre de usuario
          </label>
          <Input
            placeholder="Nombre de usuario"
            type="text"
            {...register('username')}
          />
          {errors.username && (
            <p className="text-red-500 text-sm mt-1">{errors.username.message}</p>
          )}
        </div>

        {/* Campo de Email */}
        <div className="space-y-2">
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
            Correo electrónico
          </label>
          <Input
            placeholder="Escriba su correo electrónico"
            type="email"
            {...register('email')}
          />
          {errors.email && (
            <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>
          )}
        </div>

        {/* Campo de Nombre */}
        <div className="space-y-2">
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
            Nombre
          </label>
          <Input
            placeholder="Escriba su nombre"
            type="text"
            {...register('first_name')}
          />
          {errors.first_name && (
            <p className="text-red-500 text-sm mt-1">{errors.first_name.message}</p>
          )}
        </div>

        {/* Campo de Apellido */}
        <div className="space-y-2">
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
            Apellidos
          </label>
          <Input
            placeholder="Escriba sus apellidos"
            type="text"
            {...register('last_name')}
          />
          {errors.last_name && (
            <p className="text-red-500 text-sm mt-1">{errors.last_name.message}</p>
          )}
        </div>

        {/* Campo de Contraseña */}
        <div className="space-y-2">
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
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
          {errors.password && (
            <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>
          )}
        </div>

        {/* Campo de Confirmar Contraseña */}
        <div className="space-y-2">
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
            Escriba su contraseña de nuevo
          </label>
          <div className="relative">
            <Input
              placeholder="Confirmar Contraseña"
              type={showRePassword ? "text" : "password"}
              {...register('re_password')}
            />
            <Button
              variant="ghost"
              className="cursor-pointer absolute right-0 top-1/2 transform -translate-y-1/2"
              type="button"
              onClick={() => setShowRePassword(!showRePassword)}
            >
              {showRePassword ? (
                <EyeIcon className="w-5 h-5" />
              ) : (
                <EyeOffIcon className="w-5 h-5" />
              )}
            </Button>
          </div>
          {errors.re_password && (
            <p className="text-red-500 text-sm mt-1">{errors.re_password.message}</p>
          )}
        </div>

        <Link to="/signin" className="text-sm text-center">
          ¿Ya tienes una cuenta?
        </Link>

        <Button type="submit">
          {isLoading && <Loader2 className="animate-spin" />}
          Registrarme
        </Button>
      </div>
    </form>
  )
}