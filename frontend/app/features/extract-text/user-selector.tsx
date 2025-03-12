import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "~/components/ui/select"

interface Props {
  users: string[]
}

const UserSelector = ({ users }: Props) => {
  return ( 
  <Select defaultValue={users.length > 0 ? users[0] : undefined}>
    <SelectTrigger className="w-[180px]">
      <SelectValue placeholder="Usuario" />
    </SelectTrigger>
    <SelectContent>
      {users.map(user => (
        <SelectItem key={user} value={user}>{user}</SelectItem>
      ))}
    </SelectContent>
  </Select>
  );
}
 
export default UserSelector;