type ClassificationType = 
  | 'sugerencia' 
  | 'pregunta' 
  | 'ofensa' 
  | 'queja' 
  | 'denuncia' 
  | 'criterio_general';

// Interfaz para el objeto principal de la respuesta
interface ClassificationItem {
  name: ClassificationType;
  value: number;
  color: string;
}

// Interfaz principal de respuesta
export interface ApiCommentStatsResponse {
  comments_by_classification: ClassificationItem[];
  statistics: {
    total_comments: number;
    classified_comments: number;
    unclassified_comments: number;
    urgent_comments: number;
    new_unread_comments: number;
    comments_last_month: number;
    percentage_last_month_vs_total: number;
    percentage_classified_vs_total: number;
    percentage_unclassified_vs_total: number;
    percentage_urgent_vs_classified: number;
  };
  classification_timeline: Array<{
    date: string; // Formato YYYY-MM-DD
  } & Record<ClassificationType, number>>;
}