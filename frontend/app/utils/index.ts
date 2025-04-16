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