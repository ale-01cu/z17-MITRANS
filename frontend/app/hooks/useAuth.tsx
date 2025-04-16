import { useEffect, useState, type ReactNode } from "react";
import getUsersMe from "~/api/auth/get-users-me-api";
import { createContext, useContext } from "react";
import { type User } from "~/types/user";
import { useLocation } from "react-router";
import useIsSuperuser from "./useIsSuperuser";


interface AuthContextType {
  user: User | null;
  isLoading: boolean;
}

// 1. Crear el Contexto (como lo tenías, está bien)
// Define la "forma" de los datos y un valor por defecto
const UserContext = createContext<AuthContextType>({
  user: null,         // Objeto del usuario o null
  isLoading: true,    // Estado de carga inicial
  // Podrías añadir funciones aquí si las necesitas (login, logout, etc.)
  // login: (userData) => {},
  // logout: () => {},
});

interface UserProviderProps {
  children: ReactNode;
}

// 2. Crear el Componente Provider
export const UserProvider = ({ children }: UserProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true); // Empezamos asumiendo que cargamos
  const { pathname } = useLocation();
  const [ isSuperuser, setIsSuperuser ] = useState<boolean>(false);
  const [ isManager, setIsManager ] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true; // Flag para evitar actualizaciones en componente desmontado

    const loadUser = async () => {
      try {
        // Intenta cargar desde localStorage primero
        // const storedUser = localStorage.getItem('authUser');
        const storedUser = false
        if (storedUser) {
          if (isMounted) {
            setUser(JSON.parse(storedUser));
            // Podrías considerar llamar a la API aquí también para refrescar datos,
            // o solo depender de localStorage para la carga inicial.
            // Por ahora, si está en localStorage, terminamos la carga.
             setIsLoading(false);
          }
        } else {
          // Si no está en localStorage, llama a la API
          console.log("No user in localStorage, fetching from API...");
          const data = await getUsersMe();
          setIsSuperuser(data?.is_superuser)
          if (isMounted) {
            console.log("User fetched from API:", data);
            setUser(data);
            localStorage.setItem('authUser', JSON.stringify(data)); // Guarda en localStorage
          }
        }
      } catch (error) {
        console.error("Error loading user:", error);
        // Si cualquier paso falla (localStorage o API), limpiamos
        localStorage.removeItem('authUser');
        if (isMounted) {
          setUser(null); // Asegura que el usuario es null si hay error
        }
      } finally {
        // Marca la carga como completada independientemente del resultado
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadUser();

    // Cleanup function: se ejecuta cuando el componente se desmonta
    return () => {
      isMounted = false;
    };
  }, []); // El array vacío [] asegura que esto se ejecute solo una vez al montar

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
  if(pathname === '/extract' && !isSuperuser) 
    return null
  
   return (
     <UserContext.Provider value={value}>
       {!isLoading ? children : null /* O un componente de carga */}
     </UserContext.Provider>
   );
};

// 3. Crear el Hook Personalizado para consumir el contexto
export const useAuth = () => {
  const context = useContext(UserContext);
  console.log({context});
  
  if (context === undefined) {
    // Error útil si se intenta usar fuera del Provider
    throw new Error('useAuth debe ser usado dentro de un UserProvider');
  }
  return context; // Devuelve { user, isLoading, ... }
};