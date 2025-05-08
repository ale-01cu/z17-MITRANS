import { useAuth } from "./useAuth";

const useIsSuperuser = () => {
  const { user } = useAuth();
  console.log({user});
  
  return user?.is_superuser;
}
 
export default useIsSuperuser;