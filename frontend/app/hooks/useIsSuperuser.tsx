import { useAuth } from "./useAuth";

const useIsSuperuser = () => {
  const { user } = useAuth();
  return user?.is_superuser;
}
 
export default useIsSuperuser;