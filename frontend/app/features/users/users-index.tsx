import UsersList from "./users-list"
import { useState, useMemo, useEffect } from "react"
import UsersSearchAndFilters from "./users-search-and-filters"
import UsersEditUserDialog from "./users-edit-user-dialog"
import { toast } from "sonner" 
import type { User } from "~/types/user"
import getUsersListApi from "~/api/auth/get-users-list-api"
import AddUser from "./users-add-user"
import { getRoleText, SUPERUSER_TEXT_ROLE, STAFF_TEXT_ROLE } from "./users-utils"
import type { FormErrors, UserFormData } from "./users-types"
import postCreateUsersApi from "~/api/auth/post-create-user-api"
import putUsersApi from "~/api/auth/put-users-api"

export default function UsersIndex() {
    const [users, setUsers] = useState<User[]>([])
    const [searchTerm, setSearchTerm] = useState("")
    const [departmentFilter, setDepartmentFilter] = useState<string>("all")
    const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
    const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
    const [editingUser, setEditingUser] = useState<User | null>(null)
    const [formData, setFormData] = useState<UserFormData>({
      id: null,
      externalId: "",
      username: "",
      firstName: "",
      lastName: "",
      email: "",
      role: "",
      status: true,
      password: "",
      re_password: ""
    })
    const [formErrors, setFormErrors] = useState<FormErrors>({})
    const [isLoading, setIsLoading] = useState(false)

    useEffect(() => {
      setIsLoading(true)
      getUsersListApi()
        .then(data => setUsers(data.results))
        .catch()
        .finally(() => setIsLoading(false))
    }, [])
  
    // Filtered and searched users with optimized performance
    const filteredUsers = useMemo(() => {
      return users.filter((user) => {
        const matchesSearch =
          searchTerm === "" ||
          user.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          user.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
          user.role.toLowerCase().includes(searchTerm.toLowerCase())
  
  
        return !!matchesSearch
      })
    }, [users, searchTerm, departmentFilter])
  
    // Statistics
    const stats = useMemo(() => {
      const total = users.length
      const active = users.filter((u) => u.is_active).length
      const inactive = users.filter((u) => !u.is_active).length
      return { total, active, inactive }
    }, [users])
  
    // Form validation
    const validateForm = (data: UserFormData): FormErrors => {
      const errors: FormErrors = {}
  
      // if (!data.firstName.trim()) {
      //   errors.firstName = "First name is required"
      // } else if (data.firstName.length < 2) {
      //   errors.firstName = "First name must be at least 2 characters"
      // }
  
      // if (!data.lastName.trim()) {
      //   errors.lastName = "Last name is required"
      // } else if (data.lastName.length < 2) {
      //   errors.lastName = "Last name must be at least 2 characters"
      // }
  
      // if (!data.email.trim()) {
      //   errors.email = "Email is required"
      // } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      //   errors.email = "Please enter a valid email address"
      // }

      if(editingUser && !data.role.trim()) {
        errors.role = "El rol es requerido."
      }

  
      // if (!data.role) {
      //   errors.role = "Role is required"
      // }
  
      return errors
    }
  
    // Check for duplicate email
    const isDuplicateEmail = (email: string, excludeId?: string): boolean => {
      return users.some((user) => user.email.toLowerCase() === email.toLowerCase() && user.external_id !== excludeId)
    }
  
    // Reset form
    const resetForm = () => {
      setFormData({
        id: null,
        externalId: "",
        username: "",
        firstName: "",
        lastName: "",
        email: "",
        role: "",
        status: true,
        password: "",
        re_password: ""
      })
      setFormErrors({})
    }
  
    // Create user
    const handleCreateUser = async () => {
      // e.preventDefault()
      const errors = validateForm(formData)
      console.log({errors});
      
  
      if (isDuplicateEmail(formData.email)) {
        errors.email = "Ya existe un usuario con ese email."
      }
  
      if (Object.keys(errors).length > 0) {
        setFormErrors(errors)
        return
      }
  
      setIsLoading(true)
  
      try {
        const newUser: User = {
          id: null,
          external_id: Date.now().toString(),
          username: formData.username,
          email: formData.email,
          role: formData.role === SUPERUSER_TEXT_ROLE ? 'superuser' : formData.role === STAFF_TEXT_ROLE ? 'manager' : 'consultant',
          first_name: formData.firstName,
          last_name: formData.lastName,
          is_active: false,
          is_superuser: formData.role === SUPERUSER_TEXT_ROLE,
          is_staff: formData.role === STAFF_TEXT_ROLE,
          create_at: new Date().toString(),
        }

        await postCreateUsersApi({
          ...newUser, 
          password: formData.password, 
          re_password: formData.re_password
        })
        
        setUsers((prev) => [...prev, newUser])
        setIsCreateDialogOpen(false)
        resetForm()
  
        toast("Usuario creado correctamente.", {
          description: `${formData.firstName} ${formData.lastName} ha sido agregado al sistema.`,
          style: { backgroundColor: "#17c964" },
        })
      } catch (error) {
        toast("Error creando al usuario", {
          description: "Hubo un error creando al usuario. Por favor intentelo de nuevo.",
          style: { backgroundColor: "#f31260" },
        })
      } finally {
        setIsLoading(false)
      }
    }
  
    // Edit user
    const handleEditUser = (user: User) => {
      setEditingUser(user)
      setFormData({
        username: user.username,
        firstName: user.first_name,
        lastName: user.last_name,
        email: user.email,
        role: getRoleText({ isSuperuser: user.is_superuser, isStaff: user.is_staff }),
        status: user.is_active,
        externalId: user.external_id,
        id: user.id,
        password: "",
        re_password: ""
      })
      setFormErrors({})
      setIsEditDialogOpen(true)
    }
  
    // Update user
    const handleUpdateUser = async () => {
      // e.preventDefault()
      if (!editingUser) return
  
      const errors = validateForm(formData)
  
      if (isDuplicateEmail(formData.email, editingUser.external_id)) {
        errors.email = "Ya existe un usuario con este correo"
      }
  
      if (Object.keys(errors).length > 0) {
        setFormErrors(errors)
        return
      }
  
      setIsLoading(true)
  
      try {
        // Simulate API call
        await putUsersApi({
          email: formData.email,
          first_name: formData.firstName,
          is_active: formData.status,
          is_staff: formData.role === STAFF_TEXT_ROLE,
          is_superuser: formData.role === SUPERUSER_TEXT_ROLE,
          last_name: formData.lastName,
          username: formData.username,
        }, formData?.id)
  
        setUsers((prev) =>
          prev.map((user) => (user.external_id === editingUser.external_id 
            ? { 
              ...user, 
              email: formData.email, 
              first_name: formData.firstName, 
              is_active: formData.status, 
              is_staff: formData.role === STAFF_TEXT_ROLE,
              is_superuser: formData.role === SUPERUSER_TEXT_ROLE,
              last_name: formData.lastName,
              username: formData.username,
            } 
            : user
          )),
        )
  
        setIsEditDialogOpen(false)
        setEditingUser(null)
        resetForm()
  
        toast("Usuario actualizado correctamente.", {
          description: `La información de ${formData.firstName} ${formData.lastName} ha sido actualizada.`,
          style: { backgroundColor: "#17c964" },
        })
      } catch (error) {
        toast("Error actualizando al usuario", {
          description: "Hubo un error actualizando el usuario. Por favor intentelo de nuevo.",
          style: { backgroundColor: "#f31260" },
        })
      } finally {
        setIsLoading(false)
      }
    }
  
    // Delete user
    const handleDeleteUser = async (user: User) => {
      setIsLoading(true)
  
      try {
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 500))
  
        setUsers((prev) => prev.filter((u) => u.external_id !== user.external_id))
  
        toast("User deleted successfully", {
          description: `${user.first_name} ${user.first_name} has been removed from the system.`,
          style: { backgroundColor: "#17c964" },
        })
      } catch (error) {
        toast("Error deleting user", {
          description: "There was an error deleting the user. Please try again.",
          style: { backgroundColor: "#f31260" },
        })
      } finally {
        setIsLoading(false)
      }
    }
  
    return (
      <div className="container mx-auto py-10 space-y-4">
        {/* Header */}
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Gestion de Usuarios</h1>
            <p className="text-muted-foreground">Gestion de los usuarios y su información</p>
          </div>
          <AddUser
            formData={formData}
            handleCreateUser={handleCreateUser}
            isCreateDialogOpen={isCreateDialogOpen}
            isLoading={isLoading}
            resetForm={resetForm}
            setFormData={setFormData}
            setIsCreateDialogOpen={setIsCreateDialogOpen}
          />
        </div>
  
        {/* Search and Filters */}
        <UsersSearchAndFilters 
          searchTerm={searchTerm} 
          setSearchTerm={setSearchTerm} 
        />
  
        {/* Users Table */}
        <UsersList 
            users={filteredUsers}
            handleEditUser={handleEditUser} 
            handleDeleteUser={handleDeleteUser}
            searchTerm={searchTerm}
        />
  
        {/* Edit User Dialog */}
        <UsersEditUserDialog 
          formData={formData}
          formErrors={formErrors}
          handleUpdateUser={handleUpdateUser}
          isEditDialogOpen={isEditDialogOpen}
          isLoading={isLoading}
          setFormData={setFormData}
          setIsEditDialogOpen={setIsEditDialogOpen}
        />
      </div>
    )
  }
  