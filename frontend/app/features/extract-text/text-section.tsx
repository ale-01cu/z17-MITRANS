import { Card } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { CheckSquare, XSquare } from "lucide-react";
import { Checkbox } from "~/components/ui/checkbox";
import { Label } from "~/components/ui/label";
import UserSelector from "./user-selector";

interface Statement {
  id: string,
  text: string;          // El texto del statement
  classification: string | null; // La clasificación (inicialmente vacía)
}

interface Props {
  selectAll: () => void,
  deselectAll: () => void,
  extractedStatements: Statement[],
  extractedUsers: string[],
  selectedStatements: Statement[],
  toggleStatement: (statement: Statement) => void
}

const TextSection = ({ 
  selectAll, 
  deselectAll, 
  extractedStatements, 
  extractedUsers,
  selectedStatements, 
  toggleStatement }: Props
) => {

  return ( 
    <div className="lg:col-span-2">
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Texto extraido</h2>
          <div className="flex space-x-2">
            <div className="flex gap-4">
              <Label>Usuario</Label>
              <UserSelector users={extractedUsers}/>
            </div>
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
            <div key={statement.id} className="flex justify-between">
              <div key={index} className="flex items-center space-x-3 py-2 border-b last:border-0 cursor-pointer">
                <Checkbox
                  id={`statement-${index}`}
                  checked={selectedStatements.map(s => s.text).includes(statement.text)}
                  onCheckedChange={() => toggleStatement(statement)}
                />
                <Label htmlFor={`statement-${index}`} className="cursor-pointer text-sm leading-relaxed w-full">
                  {statement.text}
                </Label>
              </div>

              {statement.classification && 
                <div className="flex gap-2 items-center">
                  <Label className="text-sm leading-relaxed w-full">
                    Clasificación:
                  </Label>
                  <span className="text-sm">Neutral</span>
                </div>
              }
            </div>
          ))}
        </div>

        <div className="mt-4 text-sm text-muted-foreground">
          {selectedStatements.length} de {extractedStatements.length} Opiniones seleccionadas
        </div>
      </Card>
    </div>
   );
}
 
export default TextSection;