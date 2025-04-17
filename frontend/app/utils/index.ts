export function formatUserFriendlyDate(isoDate: string): string {
    const date = new Date(isoDate);
    
    return new Intl.DateTimeFormat('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZone: 'UTC'  // Opcional: si quieres mantener la zona horaria original
    }).format(date);
  }

export const transformDate = (fecha: string, formato = 'YYYY-MM-DD HH:MM') => {
  const date = new Date(fecha) // Crear un objeto Date a partir de la fecha de entrada
  const year = date.getFullYear() // Obtener el year
  const month = (date.getMonth() + 1).toString().padStart(2, '0') // Obtener el month (0-indexado)
  const day = date.getDate().toString().padStart(2, '0') // Obtener el día
  const hour = date.getHours().toString().padStart(2, '0') // Obtener la hour
  const minutes = date.getMinutes().toString().padStart(2, '0') // Obtener los minutes

  // Formatear la fecha según el formato proporcionado
  let fechaFormateada = formato
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('MM', minutes) // Reemplazar minutos después de la hora para evitar conflictos

  return fechaFormateada // Retornar la fecha formateada
}

  interface ColorScheme {
    ofensa: string; // Representa un color en formato hexadecimal
    pregunta: string;
    denuncia: string;
    sugerencia: string;
    criterio_general: string;
    queja: string;
  }


export const getClassificationColor = (classification: keyof ColorScheme | undefined) => {
  const color: ColorScheme = {
    ofensa: '#FF4D4D',        // Rojo fuerte
    pregunta: '#4287F5',      // Azul claro
    denuncia: '#6C3483',      // Naranja intenso
    sugerencia: '#6FCF97',    // Verde suave
    criterio_general: '#8C52FF', // Morado
    queja: '#FCE788'          // Amarillo dorado
  };

  if(!classification) return ''

  return color[classification]

}