import { useEffect, useState, type ReactNode } from "react";
import getUsersMe from "~/api/auth/get-users-me-api";
import { createContext, useContext } from "react";
import { type User } from "~/types/user";
import { useLocation } from "react-router";
import { CACHE_DURATION, CACHE_KEY, CACHE_TIMESTAMP_KEY } from "~/config"


interface AuthContextType {
  user: User | null;
  isLoading: boolean;
}



// 1. Crear el Contexto (como lo tenías, está bien)
// Define la "forma" de los datos y un valor por defecto
export const UserContext = createContext<AuthContextType>({
  user: null,         // Objeto del usuario o null
  isLoading: true,    // Estado de carga inicial
  // Podrías añadir funciones aquí si las necesitas (login, logout, etc.)
  // login: (userData) => {},
  // logout: () => {},
});



interface UserProviderProps {
  children: ReactNode;
}

const UserProvider = ({ children }: UserProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { pathname } = useLocation();
  const [ isSuperuser, setIsSuperuser ] = useState<boolean>(false);
  const [ isManager, setIsManager ] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;

    const loadUser = async () => {
      try {
        const storedUser = localStorage.getItem(CACHE_KEY);
        const storedTimestamp = localStorage.getItem(CACHE_TIMESTAMP_KEY);
        const now = Date.now();

        if (storedUser && storedTimestamp && now - Number(storedTimestamp) < CACHE_DURATION) {
          // Use cached user if not expired
          const parsedUser = JSON.parse(storedUser);
          if (isMounted) {
            setUser(parsedUser);
            setIsSuperuser(parsedUser?.is_superuser);
            setIsManager(parsedUser?.is_staff);
            setIsLoading(false);
          }
        } else {
          // Fetch from API and update cache
          const data = await getUsersMe();
          setIsSuperuser(data?.is_superuser);
          setIsManager(data?.is_staff);
          if (isMounted) {
            setUser(data);
            localStorage.setItem(CACHE_KEY, JSON.stringify(data));
            localStorage.setItem(CACHE_TIMESTAMP_KEY, now.toString());
          }
        }
      } catch (error) {
        localStorage.removeItem(CACHE_KEY);
        localStorage.removeItem(CACHE_TIMESTAMP_KEY);
        if (isMounted) {
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadUser();

    return () => {
      isMounted = false;
    };
  }, []);

  // Aquí podrías añadir funciones como login, logout que modifiquen el estado 'user'
  // const login = (userData) => { ... };
  // const logout = () => { ... };

  // El objeto 'value' que se pasará al Provider
  const value = {
    user,
    isLoading,
    // login, // Descomenta si añades la función login
    // logout, // Descomenta si añades la función logout
  };

  // Renderiza el Provider del contexto, pasando el valor
  // y asegurándose de renderizar los componentes hijos (children)
  // Solo renderiza children cuando la carga inicial ha terminado
  
  if(pathname === '/extract' && (!isSuperuser && !isManager)) 
    return null

  else if(pathname === '/bot' && (!isSuperuser && !isManager))
    return null
  
   return (
     <UserContext.Provider value={value}>
       {!isLoading ? children : null /* O un componente de carga */}
     </UserContext.Provider>
   );
};


export default UserProvider