import { Card } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { Download, Send, Tag } from "lucide-react";

interface Props {
  handleClassify: () => void
  handleDownload: () => void
  handleProcess: () => void,
  selectedStatements: string[]
}

const ActionSection = ({ 
  handleClassify, 
  handleDownload, 
  handleProcess, 
  selectedStatements }: Props
) => {

  return ( 
    <div className="h-full">
      <Card className="p-6 sticky top-7">
        <h2 className="text-xl font-semibold mb-4">Actions</h2>
        <div className="flex flex-col items-start space-y-3">
          <Button onClick={handleClassify} disabled={selectedStatements.length === 0}>
            <Tag className="h-4 w-4 mr-2" />
            Clasificar opiniones
          </Button>
          <Button variant="outline" onClick={handleDownload} disabled={selectedStatements.length === 0}>
            <Download className="h-4 w-4 mr-2" />
            Descargar seleccionados
          </Button>
          <Button variant="secondary" onClick={handleProcess} disabled={selectedStatements.length === 0}>
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