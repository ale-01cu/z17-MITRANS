const SUPERUSER_TEXT_ROLE = "Administrador"
const STAFF_TEXT_ROLE = "Gestor"
const BASE_TEXT_ROLE = "Consultor"


const getRoleText = ({ isSuperuser, isStaff }: { isSuperuser: boolean, isStaff: boolean }) => {
  if(isSuperuser) return SUPERUSER_TEXT_ROLE
  else if(isStaff && !isSuperuser) return STAFF_TEXT_ROLE
  else return BASE_TEXT_ROLE
}

export { SUPERUSER_TEXT_ROLE, STAFF_TEXT_ROLE, BASE_TEXT_ROLE, getRoleText }