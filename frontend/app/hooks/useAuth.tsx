import { useContext } from "react";
import { UserContext } from "~/context/UserProvider";


// 2. Crear el Componente Provider

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
