import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "~/components/ui/dialog"
import { Label } from "~/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select"
import { Button } from "~/components/ui/button"
import { Input } from "~/components/ui/input"
import type { FormErrors, UserFormData } from './users-types'
import { SUPERUSER_TEXT_ROLE, BASE_TEXT_ROLE, STAFF_TEXT_ROLE } from "./users-utils"

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
  handleUpdateUser: (e: React.FormEvent<HTMLFormElement>) => void
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

  console.log({formData});
  

  return (
    <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Editar Usuario</DialogTitle>
          <DialogDescription>Actualizar información del usuario. Haz cambios y salvalos cuando esten listos.</DialogDescription>
        </DialogHeader>
        <form id="edit-user-form" onSubmit={handleUpdateUser} className="grid gap-4 py-4">
          <div className="flex flex-col gap-4">
            <div className="space-y-2">
              <Label htmlFor="email">Nombre de usuario *</Label>
              <Input
                id="username"
                type="username"
                value={formData.username}
                onChange={(e) => setFormData((prev) => ({ ...prev, username: e.target.value }))}
                className={formErrors.username ? "border-red-500" : ""}
              />
              {formErrors.username && <p className="text-sm text-red-500">{formErrors.username}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="editEmail">Correo *</Label>
              <Input
                id="editEmail"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData((prev) => ({ ...prev, email: e.target.value }))}
                className={formErrors.email ? "border-red-500" : ""}
              />
              {formErrors.email && <p className="text-sm text-red-500">{formErrors.email}</p>}
            </div>

            <div className="flex gap-4">
              <div className="space-y-2">
                <Label htmlFor="editFirstName">Nombre *</Label>
                <Input
                  id="editFirstName"
                  value={formData.firstName}
                  onChange={(e) => setFormData((prev) => ({ ...prev, firstName: e.target.value }))}
                  className={formErrors.firstName ? "border-red-500" : ""}
                />
                {formErrors.firstName && <p className="text-sm text-red-500">{formErrors.firstName}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="editLastName">Apellidos *</Label>
                <Input
                  id="editLastName"
                  value={formData.lastName}
                  onChange={(e) => setFormData((prev) => ({ ...prev, lastName: e.target.value }))}
                  className={formErrors.lastName ? "border-red-500" : ""}
                />
                {formErrors.lastName && <p className="text-sm text-red-500">{formErrors.lastName}</p>}
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