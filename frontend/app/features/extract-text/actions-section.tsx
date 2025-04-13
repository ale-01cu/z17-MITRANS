import { Card } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Download, Send, Tag, Loader2 } from "lucide-react";
import { useState } from "react";
import ClassifyBtnByCommentId from "~/components/classification/classify-btn-by-comment-id";

interface Statement {
  id: string,
  text: string;          // El texto del statement
  classification: string | null; // La clasificación (inicialmente vacía)
}


interface Props {
  handleClassify: (setIsClassifying: React.Dispatch<React.SetStateAction<boolean>>) => void
  handleDownload: () => void
  handleProcess: () => void,
  selectedStatements: Statement[],
  setSelectedStatements: React.Dispatch<React.SetStateAction<Statement[]>>
}

const ActionSection = ({ 
  handleClassify, 
  handleDownload, 
  handleProcess, 
  selectedStatements,
  setSelectedStatements 
}: Props) => {
  const [ isClassifying, setIsClassifying ] = useState(false)

  return ( 
    <div className="h-full">
      <Card className="p-6 sticky top-7">
        <h2 className="text-xl font-semibold mb-4">Acciones</h2>
        <div className="flex flex-col items-start space-y-3">
          <ClassifyBtnByCommentId 
            comments={selectedStatements}
            setComments={setSelectedStatements}
          />
          <Button className="w-full flex justify-start" variant="outline" onClick={handleDownload} disabled={selectedStatements.length === 0}>
            <Download className="h-4 w-4 mr-2" />
            Exportar a Excel
          </Button>
          <Button className="w-full flex justify-start" variant="secondary" onClick={handleProcess} disabled={selectedStatements.length === 0}>
            <Send className="h-4 w-4 mr-2" />
            Procesar opiniones
          </Button>

          {/* Additional action buttons can be added here */}
        </div>
      </Card>
    </div>
  );
}
 
export default ActionSection;