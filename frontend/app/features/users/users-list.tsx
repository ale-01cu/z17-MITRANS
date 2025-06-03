import { Users } from "lucide-react";
import { Card, CardContent } from "~/components/ui/card";
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from "~/components/ui/table";
import { Badge } from "~/components/ui/badge";
import { Button } from "~/components/ui/button";
import { Edit, } from "lucide-react";
import type { User } from "~/types/user";
import { getRoleText } from "./users-utils";

interface UsersListProps {
  users: User[]
  handleEditUser: (user: User) => void
  handleDeleteUser: (user: User) => Promise<void>
  searchTerm: string
}

export default function UsersList({ users, handleEditUser, handleDeleteUser, searchTerm }: UsersListProps) {
    return (
      <div>
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nombre de usuario</TableHead>
                    <TableHead>Nombre Completo</TableHead>
                    <TableHead>Rol</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead>Fecha de creación</TableHead>
                    <TableHead className="text-right">Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} className="text-center py-8">
                        <div className="flex flex-col items-center space-y-2">
                          <Users className="h-8 w-8 text-muted-foreground" />
                          <p className="text-muted-foreground">
                            {searchTerm
                              ? "No se encontraron usuarios para el criterio de busqueda."
                              : "No se encontraron usuarios."}
                          </p>
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    users.map((user) => (
                      <TableRow key={user.external_id}>
                        <TableCell className="font-medium">
                          {user.username}
                        </TableCell>
                        <TableCell>{user.first_name} {user.last_name}</TableCell>
                        <TableCell>{getRoleText({isStaff: user.is_staff, isSuperuser: user.is_superuser})}</TableCell>
                        <TableCell>
                          <Badge 
                            className={user.is_active ? 'bg-emerald-500' : 'bg-red-500 text-white' } 
                            variant={user.is_active ? "default" : "secondary"}
                          >
                            {user.is_active ? "Activo" : "Inactivo"}
                          </Badge>
                        </TableCell>
                        <TableCell>{new Date(user.created_at).toLocaleDateString()}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end space-x-2">
                            <Button variant="outline" size="sm" onClick={() => handleEditUser(user)}>
                              <Edit className="h-4 w-4" />
                            </Button>
                            {/* <AlertDialog>
                              <AlertDialogTrigger asChild>
                                <Button variant="outline" size="sm">
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </AlertDialogTrigger>
                              <AlertDialogContent>
                                <AlertDialogHeader>
                                  <AlertDialogTitle>¿ Está seguro de eliminar el usuario ?</AlertDialogTitle>
                                  <AlertDialogDescription>
                                    This action cannot be undone. This will permanently delete{" "}
                                    <strong>
                                      {user.firstName} {user.lastName}
                                    </strong>{" "}
                                    from the system.
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                                  <AlertDialogAction
                                    onClick={() => handleDeleteUser(user)}
                                    className="bg-red-600 hover:bg-red-700"
                                  >
                                    Delete User
                                  </AlertDialogAction>
                                </AlertDialogFooter>
                              </AlertDialogContent>
                            </AlertDialog> */}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    )
}