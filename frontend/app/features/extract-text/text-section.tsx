import { Card } from "~/components/ui/card";
import { Button } from "~/components/ui/button";
import { CheckSquare, XSquare, Edit2, Save } from "lucide-react";
import { Checkbox } from "~/components/ui/checkbox";
import { Label } from "~/components/ui/label";
import React, { useState } from "react";
import { Textarea } from "~/components/ui/textarea";

interface Classification {
  id: string,
  name: string
}

interface Statement {
  id: string,
  text: string;
  classification: Classification | null;
}

interface Props {
  selectAll: () => void,
  deselectAll: () => void,
  extractedStatements: Statement[],
  extractedUsers: string[],
  selectedStatements: Statement[],
  toggleStatement: (statement: Statement) => void,
  setExtractedStatements?: React.Dispatch<React.SetStateAction<Statement[]>>, // <-- Add this prop in parent!
  setSelectedStatements?: React.Dispatch<React.SetStateAction<Statement[]>>,   // <-- Add this prop in parent!
}

const TextSection = ({
  selectAll,
  deselectAll,
  extractedStatements,
  selectedStatements,
  toggleStatement,
  setExtractedStatements,
  setSelectedStatements
}: Props) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState<string>("");

  // Start editing
  const handleEdit = (statement: Statement) => {
    setEditingId(statement.id);
    setEditValue(statement.text);
  };

  // Save edit
  const handleSave = (statement: Statement) => {
    if (!setExtractedStatements) return;
    setExtractedStatements(prev =>
      prev.map(s =>
        s.id === statement.id ? { ...s, text: editValue } : s
      )
    );
    // Also update selectedStatements if needed
    if (setSelectedStatements) {
      setSelectedStatements(prev =>
        prev.map(s =>
          s.id === statement.id ? { ...s, text: editValue } : s
        )
      );
    }
    setEditingId(null);
    setEditValue("");
  };

  // Merge selected statements
  const handleMerge = () => {
    if (!setExtractedStatements || !setSelectedStatements) return;
    if (selectedStatements.length < 2) return;

    const mergedText = selectedStatements.map(s => s.text).join(" ");
    const mergedStatement: Statement = {
      id: Date.now().toString(),
      text: mergedText,
      classification: null
    };

    setExtractedStatements(prev =>
      [
        mergedStatement, // <-- Now at the beginning
        ...prev.filter(s => !selectedStatements.some(sel => sel.id === s.id))
      ]
    );
    setSelectedStatements([mergedStatement]);
  };

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
            <Button
              variant="outline"
              size="sm"
              onClick={handleMerge}
              disabled={selectedStatements.length < 2}
            >
              Unir seleccionados
            </Button>
          </div>
        </div>

        <div className="border rounded-md p-4 max-h-[500px] overflow-y-auto">
          {extractedStatements.map((statement, index) => (
            <div key={statement.id} className="flex justify-between">
              <div className="flex w-full items-center space-x-3 py-2 border-b last:border-0 cursor-pointer">
                <Checkbox
                  id={`statement-${index}`}
                  checked={selectedStatements.map(s => s.id).includes(statement.id)}
                  onCheckedChange={() => toggleStatement(statement)}
                />
                {editingId === statement.id ? (
                  <>
                    <Textarea
                      className="border px-2 py-1 rounded w-full"
                      value={editValue}
                      onChange={e => setEditValue(e.target.value)}
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleSave(statement)}
                    >
                      <Save className="h-4 w-4" />
                    </Button>
                  </>
                ) : (
                  <>
                    <Label htmlFor={`statement-${index}`} className="cursor-pointer text-sm leading-relaxed w-full">
                      {statement.text}
                    </Label>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleEdit(statement)}
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                  </>
                )}
              </div>
              {selectedStatements.map(s => s.id).includes(statement.id) &&
                selectedStatements.find(e => e.id === statement.id)?.classification &&
                <div className="flex gap-2 items-center">
                  <Label className="text-sm leading-relaxed w-full">
                    Clasificación:
                  </Label>
                  <span className="text-sm">
                    {selectedStatements.find(e => e.id === statement.id)?.classification?.name}
                  </span>
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
};

export default TextSection;