import { Card } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { CheckSquare, XSquare } from "lucide-react";
import { Checkbox } from "~/components/ui/checkbox";
import { Label } from "~/components/ui/label";

interface Props {
  selectAll: () => void,
  deselectAll: () => void,
  extractedStatements: string[],
  selectedStatements: string[],
  toggleStatement: (statement: string) => void
}

const TextSection = ({ 
  selectAll, 
  deselectAll, 
  extractedStatements, 
  selectedStatements, 
  toggleStatement }: Props
) => {

  return ( 
    <div className="lg:col-span-2">
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Texto extraido</h2>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm" onClick={selectAll}>
              <CheckSquare className="h-4 w-4 mr-2" />
              Seleccionar todo
            </Button>
            <Button variant="outline" size="sm" onClick={deselectAll}>
              <XSquare className="h-4 w-4 mr-2" />
              Deseleccionar todo
            </Button>
          </div>
        </div>

        <div className="border rounded-md p-4 max-h-[500px] overflow-y-auto">
          {extractedStatements.map((statement, index) => (
            <div key={index} className="flex items-start space-x-3 py-2 border-b last:border-0">
              <Checkbox
                id={`statement-${index}`}
                checked={selectedStatements.includes(statement)}
                onCheckedChange={() => toggleStatement(statement)}
              />
              <Label htmlFor={`statement-${index}`} className="cursor-pointer text-sm leading-relaxed">
                {statement}
              </Label>
            </div>
          ))}
        </div>

        <div className="mt-4 text-sm text-muted-foreground">
          {selectedStatements.length} of {extractedStatements.length} Opiniones seleccionadas
        </div>
      </Card>
    </div>
   );
}
 
export default TextSection;