import { useAuth } from "./useAuth";

const useIsManager = () => {
  const { user } = useAuth();
  return user?.is_staff;
}
 
export default useIsManager;