import { useAuth } from "./useAuth";

const useIsConsultant = () => {
  const { user } = useAuth();
  const isSuperuser = user?.is_superuser;
  const isManager = user?.is_staff;
  return !isSuperuser && !isManager;
}
 
export default useIsConsultant;