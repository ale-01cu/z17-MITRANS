import createCommentListApi from "~/api/comments/create-comment-list-api";
import { Loader2, Send } from "lucide-react";
import { Button } from "../ui/button";
import { useState } from "react";
import { toast } from "sonner";

interface Classification {
  id: string,
  name: string
}

interface Statement {
  id: string,
  text: string;          // El texto del statement
  classification: Classification | string | null; // La clasificación (inicialmente vacía)
}

interface Props {
  comments: Statement[],
}

const SaveCommentsBtn = ({ comments }: Props) => {
  const [ isLoading, setIsLoading ] = useState(false)


  const handleClick = () => {
    setIsLoading(true)
    createCommentListApi(comments.map(e => ({
      text: e.text,
      classification_id: 
      typeof e.classification === 'string' ? e.classification :
        e.classification?.id ? e.classification.id.toString() :
        null
    })))
      .then(() => {
        toast.success("Las opiniones han sido guardadas correctamente.")
      })
      .catch(e => {
        console.error(e)
        toast.error('Ha ocurrido un error al guardar las opiniones.')
      })
      .finally(() => {
        setIsLoading(false)
      })
  }

  return ( 
    <Button 
      className="w-full flex justify-center" 
      variant="secondary" 
      onClick={handleClick} 
      disabled={comments.length === 0}
    >
      {isLoading ? (
        <div className="flex items-center">
          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          Guardando...
        </div>
      ) : (
        <div className="flex items-center">
          <Send className="h-4 w-4 mr-2" />
          Guardar opiniones
        </div>
      )}
    </Button>
   );
}
 
export default SaveCommentsBtn;