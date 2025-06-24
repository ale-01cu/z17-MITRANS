import type React from "react";
import { Button } from "~/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "~/components/ui/dialog";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import type { UserOwner, UserOwnerPut } from "~/types/user-owner";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import putUserOwnerApi from "~/api/user-owner/put-user-owner-api";
import { toast } from "sonner";
import { QueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { Loader2 } from "lucide-react";

const queryClient = new QueryClient()

export const userOwnerSchema = z.object({
  // name: z.string().min(1, "El nombre es requerido"),
  email: z.string().email("Debe ser un email válido").optional().or(z.literal("")),
  phone_number: z.string().optional(),
  province: z.string().optional(),
});

interface Props {
  isEditDialogOpen: boolean
  setIsEditDialogOpen: React.Dispatch<React.SetStateAction<boolean>>
  userOwner: UserOwner | null
}

export default function UserOwnerEdit({ isEditDialogOpen, setIsEditDialogOpen, userOwner }: Props) {
  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<UserOwnerPut>({
    resolver: zodResolver(userOwnerSchema),
  });

  useEffect(() => {
    if (userOwner) {
      setValue("email", userOwner.email)
      setValue("phone_number", userOwner.phone_number)
      setValue("province", userOwner.province)
    }
  }, [userOwner])

  const onSubmit = async (data: UserOwnerPut) => {
    try {
      await putUserOwnerApi({id: userOwner?.id || "", data})
      toast.success('Se ha actualizado correctamente.')
      setIsEditDialogOpen(false)
      queryClient.invalidateQueries({ queryKey: ["user-owners"] })
      queryClient.invalidateQueries({ queryKey: ['comments'] })

    } catch (error) {
      toast.error('Ocurrio un error al actualizar el usuario.')
      console.error("Error updating user owner:", error)
    }
  }

  return (
    <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Editar Usuario Emisor</DialogTitle>
          <DialogDescription>Puede modificar el campo que desee del usuario seleccionado.</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Campo Nombre */}
          {/* <div className="space-y-2">
            <Label>Nombre</Label>
            <Input {...register("name")} placeholder="Nombre del usuario" />
            {errors.name && <p className="text-red-500 text-sm">{errors.name.message}</p>}
          </div> */}

          {/* Campo Email */}
          <div className="space-y-2">
            <Label>Email</Label>
            <Input {...register("email")} placeholder="Email del usuario" />
            {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}
          </div>

          {/* Campo Teléfono */}
          <div className="space-y-2">
            <Label>Teléfono</Label>
            <Input {...register("phone_number")} placeholder="Teléfono del usuario" />
          </div>

          {/* Campo Provincia */}
          <div className="space-y-2">
            <Label>Provincia</Label>
            <Input {...register("province")} placeholder="Provincia del usuario" />
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" type="button" onClick={() => setIsEditDialogOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit">
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin"/>}
              {isSubmitting ? "Actualizando..." : "Actualizar"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}