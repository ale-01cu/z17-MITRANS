import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select"
import { use, useEffect, useState } from "react";
import listUserOwnerApi from "~/api/user-owner/list-user-owner-api";
import type { userOwner } from "~/types/user-owner";


interface UserOwnerSelectorProps {
  value: string
  handleChange: (value: string) => void,
  error?: boolean
}


const UserOwnerSelector = ({ value, handleChange, error }: UserOwnerSelectorProps) => {
  const [ users, setUsers ] = useState<userOwner[]>([])

  useEffect(() => {
    listUserOwnerApi()
      .then(data => setUsers(data.results))
      .catch(e => console.error(e))
  }, [])

  console.log({users});
  

  return ( 
    <div>
      <Select value={value} onValueChange={handleChange}>
        <SelectTrigger id="usuario" className={`w-full ${error ? "border-red-500" : ""}`}>
          <SelectValue placeholder="Seleccione un usuario" />
        </SelectTrigger>
        <SelectContent>
          {users.map((user) => (
            <SelectItem key={user.id} value={user.name}>
              {user.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {error && <p className="text-sm text-red-500">El usuario es requerido</p>}
    </div>
  );
}
 
export default UserOwnerSelector;