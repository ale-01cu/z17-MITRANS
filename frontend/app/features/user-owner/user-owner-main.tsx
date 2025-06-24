import UserOwnerList from "./user-owner-list"
import { useState } from "react"
import UserOwnerEdit from "./user-owner-edit"
import type { UserOwner } from "~/types/user-owner"
import { Search } from "lucide-react"
import { Card, CardContent } from "~/components/ui/card"
import { Input } from "~/components/ui/input"
import { useDebounce } from "@uidotdev/usehooks"

export default function UserOwnerMain() {
  const [ isEditDialogOpen, setIsEditDialogOpen ] = useState(false)
  const [ userOwner, setUserOwner ] = useState<UserOwner | null>(null)
  const [ searchTerm, setSearchTerm ] = useState("")
  const debouncedSearchTerm = useDebounce(searchTerm, 300)

  const openEditDialog = (userOwner: UserOwner) => {
    setIsEditDialogOpen(true)
    setUserOwner(userOwner)
  }

  return (
    <main className="py-10 space-y-8">
      <header className="sticky top-0 z-10 flex h-16 items-center gap-4 bg-background">
        <div className=''>
          <h1 className="text-3xl font-bold tracking-tight">Usuarios Emisores.</h1>
          <p className="text-muted-foreground">Gestión de usuarios emisores.</p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          {/* <Button variant="outline" size="sm" className="h-8 gap-1">
            <RefreshCw className="h-3.5 w-3.5" />
            <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">Refrescar</span>
          </Button> */}
          {/* <Button variant="outline" size="sm" className="h-8 gap-1">
            <Filter className="h-3.5 w-3.5" />
            <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">Filtrar</span>
          </Button> */}
        </div>
      </header>


      <Card>
        <CardContent>
          <div className="flex flex-col space-y-4 md:flex-row md:items-center md:space-y-0 md:space-x-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search users by name, email, department, or role..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <UserOwnerList
        openEditDialog={openEditDialog}
        searchTerm={debouncedSearchTerm}
      />

      <UserOwnerEdit 
        isEditDialogOpen={isEditDialogOpen}
        setIsEditDialogOpen={setIsEditDialogOpen}
        userOwner={userOwner}
      />

    </main>
  )
}