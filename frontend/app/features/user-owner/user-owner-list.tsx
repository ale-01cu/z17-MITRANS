import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "~/components/ui/table"
import useUserOwner from "~/hooks/useUserOwner"
import { Edit, Loader } from "lucide-react"
import { transformDate } from "~/utils"
import useIsConsultant from "~/hooks/useIsConsultant"
import { Button } from "~/components/ui/button"
import type { UserOwner } from "~/types/user-owner"


interface Props {
  openEditDialog: (userOwner: UserOwner) => void
  searchTerm: string
}


export default function UserOwnerList({ openEditDialog, searchTerm }: Props) {
  const { data, isFetching } = useUserOwner(1, searchTerm)
  const isConsultant = useIsConsultant()


  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Nombre</TableHead>
          <TableHead>Correo</TableHead>
          <TableHead>Número</TableHead>
          <TableHead>Provincia</TableHead>
          <TableHead>Fecha de Creación</TableHead>
          {!isConsultant && (
            <TableHead className="text-right">Acciones</TableHead>
          )}
        </TableRow>
      </TableHeader>
      <TableBody>
        {isFetching ? (
          <TableRow>
            <TableCell colSpan={6} className="text-center w-full">
              <div className="flex items-center justify-center gap-2 py-10">
                <Loader className="w-6 h-6 animate-spin" /> Cargando Usuarios...
              </div>
            </TableCell>
          </TableRow>
        ) : data?.results.length === 0 ? (
          <TableRow>
            <TableCell colSpan={6} className="text-center w-full">
              <div className="py-10">No se encontraron Usuarios</div>
            </TableCell>
          </TableRow>
        ) : (
          data?.results.map((userOwner) => (
            <TableRow
              key={userOwner.id}
              // onClick={() => toggleComment(userOwner)} // Agregamos el evento onClick aquí
              className="" // Cambiamos el cursor para indicar que es clickeable
            >
              <TableCell className="relative min-w-0 max-w-16 xl:max-w-24 2xl:max-w-36 truncate">
                {userOwner.name}
              </TableCell>
              <TableCell>{userOwner.email || '-'}</TableCell>
              <TableCell>{userOwner.phone_number || '-'}</TableCell>
              <TableCell>{userOwner.province || '-'}</TableCell>
              <TableCell><div className="text-xs">{transformDate(userOwner.created_at)}</div></TableCell>
              {!isConsultant && (
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={(e) => {
                        e.stopPropagation(); // Evitamos que el clic en el botón active el evento de la fila
                        openEditDialog(userOwner);
                      }}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              )}
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  )  
}