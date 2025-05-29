import { EyeIcon, EyeOffIcon, Plus } from "lucide-react"
import { useState } from "react"
import { Button } from "~/components/ui/button"
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription, 
  DialogFooter, 
  DialogTrigger 
} from "~/components/ui/dialog"
import { Input } from "~/components/ui/input"
import { Label } from "~/components/ui/label"
import type { FormErrors, UserFormData } from "./users-types"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { CreateUserSchema } from "./users-schemas"


interface UsersAddUserDialogProps {
  isCreateDialogOpen: boolean, 
  setIsCreateDialogOpen: React.Dispatch<React.SetStateAction<boolean>>, 
  formData: UserFormData, 
  setFormData: React.Dispatch<React.SetStateAction<UserFormData>>, 
  handleCreateUser: () => Promise<void>,
  resetForm: () => void
  isLoading: boolean, 
}

export default function AddUser({ 
  isCreateDialogOpen, 
  setIsCreateDialogOpen, 
  resetForm, 
  formData, 
  setFormData, 
  handleCreateUser,
  isLoading 
}: UsersAddUserDialogProps) {
  const [showPassword, setShowPassword] = useState(false)
  const [showRePassword, setShowRePassword] = useState(false)
  const { register, handleSubmit, setValue, formState: { errors } } = useForm({ 
    resolver: zodResolver(CreateUserSchema) })


  const myHandleSubmit = async () => {
    await handleCreateUser()
    // setValue('username', '');
    // setValue('email', '');
    // setValue('first_name', '');
    // setValue('last_name', '');
    // setValue('password', '');
    // setValue('re_password', '');
  }

  return (
    <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
      <DialogTrigger asChild>
        <Button onClick={resetForm}>
          <Plus className="mr-2 h-4 w-4" />
          Nuevo usuario
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px] max-h-[90%] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Crear nuevo usuario</DialogTitle>
          <DialogDescription>Agregar un nuevo usuario al sistema. Rellene toda la información requerida.</DialogDescription>
        </DialogHeader>
        <form id="add-user-form" onSubmit={handleSubmit(myHandleSubmit)} className="grid gap-4 py-4">
          <div className="flex flex-col gap-4">
            <div className="space-y-2">
              <Label htmlFor="email">Nombre de usuario *</Label>
              <Input
                id="username"
                type="username"
                value={formData.username}
                className={errors.username ? "border-red-500" : ""}
                {...register('username', { onChange: (e) => setFormData((prev) => ({ ...prev, username: e.target.value })) })}
              />
              {errors.username && <p className="text-sm text-red-500">{errors.username.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="firstName">Correo *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                className={errors.email ? "border-red-500" : ""}
                {...register('email', { onChange: (e) => setFormData((prev) => ({ ...prev, email: e.target.value })) })}
              />
              {errors.email && <p className="text-sm text-red-500">{errors.email.message}</p>}
            </div>

            <div className="flex gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName">Nombre *</Label>
                <Input
                  id="firstName"
                  value={formData.firstName}
                  className={errors.first_name ? "border-red-500" : ""}
                  {...register('first_name', { onChange: (e) => setFormData((prev) => ({ ...prev, firstName: e.target.value })) })}

                />
                {errors.first_name && <p className="text-sm text-red-500">{errors.first_name.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="lastName">Apellidos *</Label>
                <Input
                  id="lastName"
                  value={formData.lastName}
                  className={errors.last_name ? "border-red-500" : ""}
                  {...register('last_name', { onChange: (e) => setFormData((prev) => ({ ...prev, lastName: e.target.value })) })}
                />
                {errors.last_name && <p className="text-sm text-red-500">{errors.last_name.message}</p>}
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <label htmlFor="username" className="block text-sm font-medium text-gray-700">
              Contraseña
            </label>
            <div className="relative">
              <Input
                placeholder="Escriba su contraseña"
                type={showPassword ? "text" : "password"}
                value={formData.password}
                {...register('password', { onChange: (e) => setFormData((prev) => ({ ...prev, password: e.target.value })) })}

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
                value={formData.re_password}
                {...register('re_password', { onChange: (e) => setFormData((prev) => ({ ...prev, re_password: e.target.value })) })}

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

          {/* <div className="space-y-2">
            <Label htmlFor="editRole">Rol *</Label>
            <Select
              value={formData.role}
              defaultValue={roles[0].name}
              onValueChange={(value) => setFormData((prev) => ({ ...prev, role: value }))}
            >
              <SelectTrigger className={formErrors.role ? "border-red-500" : ""}>
                <SelectValue placeholder="Seleccionar Rol" />
              </SelectTrigger>
              <SelectContent>
                {roles.map((role) => (
                  <SelectItem key={role.name} value={role.name}>
                    {role.name}
                  </SelectItem>
                ))}
              </SelectContent>  
            </Select>
            {formErrors.role && <p className="text-sm text-red-500">{formErrors.role}</p>}
          </div>
          
          <div className="flex items-center gap-2">
            <Label htmlFor="status">Activo</Label>
            <Checkbox name="status" id="status" onChange={() => setFormData((prev) => ({ ...prev, status: !formData.status }))} />
          </div> */}
        </form>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
            Cancelar
          </Button>
          <Button form="add-user-form" type="submit" disabled={isLoading}>
            {isLoading ? "Creando..." : "Crear Usuario"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}