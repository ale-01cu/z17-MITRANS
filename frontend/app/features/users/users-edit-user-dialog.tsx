import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription, 
  DialogFooter
} from "~/components/ui/dialog"
import { Label } from "~/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select"
import { Button } from "~/components/ui/button"
import { Input } from "~/components/ui/input"
import type { FormErrors, UserFormData } from './users-types'
import { SUPERUSER_TEXT_ROLE, BASE_TEXT_ROLE, STAFF_TEXT_ROLE } from "./users-utils"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { UpdateUserSchema } from "./users-schemas"
import { useEffect } from "react"

const roles = [
  {
    name: BASE_TEXT_ROLE,
    isSuperUser: false,
    isStaff: false
  },
  {
    name: STAFF_TEXT_ROLE,
    isSuperUser: false,
    isStaff: true
  },
  {
    name: SUPERUSER_TEXT_ROLE,
    isSuperUser: true,
    isStaff: false
  },
]

interface UsersEditUserDialogProps {
  isEditDialogOpen: boolean, 
  setIsEditDialogOpen: React.Dispatch<React.SetStateAction<boolean>>, 
  formData: UserFormData, 
  setFormData: React.Dispatch<React.SetStateAction<UserFormData>>, 
  formErrors: FormErrors, 
  isLoading: boolean, 
  handleUpdateUser: () => Promise<void>
}

export default function UsersEditUserDialog({ 
  isEditDialogOpen, 
  setIsEditDialogOpen, 
  formData, 
  setFormData, 
  formErrors, 
  isLoading, 
  handleUpdateUser 
}: UsersEditUserDialogProps) {
  const { register, handleSubmit, setValue, formState: { errors }, reset } = useForm({ 
    resolver: zodResolver(UpdateUserSchema) })

    useEffect(() => {
      if (isEditDialogOpen && formData) {
        reset({
          username: formData.username,
          email: formData.email,
          // Map to what RHF expects based on your schema/register names
          first_name: formData.firstName,
          last_name: formData.lastName,
          // role and status are not directly registered in the same way with RHF for simple inputs
          // but their values are controlled by formData and used by Select components.
          // RHF will validate based on the actual form submission.
          // If you had specific RHF validation on role/status that needed to be primed,
          // you might also call setValue for them here, but often not necessary for Selects.
        });
      }
    }, [isEditDialogOpen, formData, reset]); // <--- DEPENDENCIES


  const myHandleSubmit = async () => {
    await handleUpdateUser()
    // setValue('username', '');
    // setValue('email', '');
    // setValue('first_name', '');
    // setValue('last_name', '');
  }
  

  return (
    <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Editar Usuario</DialogTitle>
          <DialogDescription>Actualizar información del usuario. Haz cambios y salvalos cuando esten listos.</DialogDescription>
        </DialogHeader>
        <form id="edit-user-form" onSubmit={handleSubmit(myHandleSubmit)} className="grid gap-4 py-4">
          <div className="flex flex-col gap-4">
            <div className="space-y-2">
              <Label htmlFor="email">Nombre de usuario *</Label>
              <Input
                id="username"
                type="username"
                value={formData.username}
                className={formErrors.username ? "border-red-500" : ""}
                {...register('username', { onChange: (e) => setFormData((prev) => ({ ...prev, username: e.target.value })) })}
              
              />
              {errors.username?.message && <p className="text-sm text-red-500">{errors.username?.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="editEmail">Correo *</Label>
              <Input
                id="editEmail"
                type="email"
                value={formData.email}
                className={formErrors.email ? "border-red-500" : ""}
                {...register('email', { onChange: (e) => setFormData((prev) => ({ ...prev, email: e.target.value })) })}

              />
              {errors.email && <p className="text-sm text-red-500">{errors.email.message}</p>}
            </div>

            <div className="flex gap-4">
              <div className="space-y-2">
                <Label htmlFor="editFirstName">Nombre *</Label>
                <Input
                  id="editFirstName"
                  value={formData.firstName}
                  className={formErrors.firstName ? "border-red-500" : ""}
                  {...register('first_name', { onChange: (e) => setFormData((prev) => ({ ...prev, firstName: e.target.value })) })}
                />
                {errors.first_name && <p className="text-sm text-red-500">{errors.first_name.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="editLastName">Apellidos *</Label>
                <Input
                  id="editLastName"
                  value={formData.lastName}
                  className={formErrors.lastName ? "border-red-500" : ""}
                  {...register('last_name', { onChange: (e) => setFormData((prev) => ({ ...prev, lastName: e.target.value })) })}

                />
                {errors.last_name && <p className="text-sm text-red-500">{errors.last_name.message}</p>}
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="editRole">Rol *</Label>
              <Select
                value={formData.role}
                defaultValue={formData.role}
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
          </div>
          <div className="space-y-2">
            <Label htmlFor="editStatus">Estado</Label>
            <Select
              value={formData.status ? 'active': 'inactive'}
              onValueChange={(value: "active" | "inactive") => setFormData((prev) => ({ ...prev, status: value === 'active' }))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Activo</SelectItem>
                <SelectItem value="inactive">Inactivo</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </form>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => setIsEditDialogOpen(false)}>
            Cancelar
          </Button>
          <Button form="edit-user-form" type="submit" disabled={isLoading}>
            {isLoading ? "Actualizando..." : "Actualizar Usuarior"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}