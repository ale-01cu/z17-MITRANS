import postClassifyCommentApi from "~/api/classification/post-classify-comment-api";
import { toast } from "sonner";
import { useState } from "react";
import { Button } from "../ui/button";
import { Loader2, Tag } from "lucide-react";

interface Classification {
  id: string,
  name: string
}


interface Statement {
  id: string,
  text: string;          // El texto del statement
  classification: Classification | null; // La clasificación (inicialmente vacía)
}

interface Props {
  comments: Statement[],
  setComments: React.Dispatch<React.SetStateAction<Statement[]>>
}

const ClassifyByCommentTextBtn = ({ comments, setComments }: Props) => {
  const [ isClassifying, setIsClassifying ] = useState(false)


  const handleClassify = () => {
    setIsClassifying(true)
    postClassifyCommentApi(comments.map(e => {
      return {
        id: e.id,
        text: e.text
      }
    }))
      .then((data) => {
        setComments(data.data)
        toast.success('Comentarios clasificados correctamente.')
      })
      .catch(e => {
        console.error('Error get classify comment by id api: ', e)
        toast.error('No se pudieron clasificar los comentarios.')
      })
      .finally(() => setIsClassifying(false))
    }

  return ( 
    <Button 
      className=" flex justify-start w-48" 
      onClick={handleClassify} 
      disabled={comments.length === 0}
    >
      {isClassifying ? (
        <>
          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          Clasificando...
        </>
      ) : (
        <>
          <Tag className="h-4 w-4 mr-2" />
          Clasificar opiniones
        </>
      )}
    </Button>
  );
}
 
export default ClassifyByCommentTextBtn;