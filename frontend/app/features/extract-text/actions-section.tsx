import { Card } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Download } from "lucide-react";
import ClassifyByCommentTextBtn from "~/components/classification/classify-by-comment-text-btn";
import SaveCommentsBtn from "~/components/comment/save-comments-btn";

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
  handleDownload: () => void
  selectedStatements: Statement[],
  setSelectedStatements: React.Dispatch<React.SetStateAction<Statement[]>>
}

const ActionSection = ({ 
  handleDownload, 
  selectedStatements,
  setSelectedStatements 
}: Props) => {

  return ( 
    <div className="h-full">
      <Card className="p-6 sticky top-7">
        <h2 className="text-xl font-semibold mb-4">Acciones</h2>
        <div className="flex flex-col items-start space-y-3">
          <ClassifyByCommentTextBtn 
            comments={selectedStatements}
            setComments={setSelectedStatements}
          />
          {/* <Button className="w-full flex justify-start" variant="outline" onClick={handleDownload} disabled={selectedStatements.length === 0}>
            <Download className="h-4 w-4 mr-2" />
            Exportar a Excel
          </Button> */}
          <SaveCommentsBtn comments={selectedStatements}/>

          {/* Additional action buttons can be added here */}
        </div>
      </Card>
    </div>
  );
}
 
export default ActionSection;