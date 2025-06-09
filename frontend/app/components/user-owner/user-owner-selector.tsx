import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select"
import { use, useEffect, useState } from "react";
import listUserOwnerApi from "~/api/user-owner/list-user-owner-api";
import type { UserOwner } from "~/types/user-owner";


interface UserOwnerSelectorProps {
  value: string
  handleChange: (value: string) => void,
  error?: boolean
  isFilter?: boolean
  className?: string,
  newCommentCounter: number
}


const UserOwnerSelector = ({ value, handleChange, error, isFilter = false, className, newCommentCounter }: UserOwnerSelectorProps) => {
  const [ users, setUsers ] = useState<UserOwner[]>([])

  useEffect(() => {
    listUserOwnerApi()
      .then(data => setUsers(data.results))
      .catch(e => console.error(e))
  }, [newCommentCounter])

  return ( 
    <div className={className}>
      <Select value={value} onValueChange={handleChange}>
        <SelectTrigger id="usuario" className={`w-full ${error ? "border-red-500" : ""}`}>
          <SelectValue placeholder="Seleccione un usuario" />
        </SelectTrigger>
        <SelectContent>
          {isFilter && <SelectItem value="all">Todos las usuarios</SelectItem>}
          {users.map((user) => (
            <>
              <SelectItem key={user.id} value={user.id}>
                {user.name}
              </SelectItem>
            </>
          ))}
        </SelectContent>
      </Select>
      {error && <p className="text-sm text-red-500">El usuario es requerido</p>}
    </div>
  );
}
 
export default UserOwnerSelector;