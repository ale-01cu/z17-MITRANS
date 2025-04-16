import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select"
import { useEffect, useState } from "react";
import { Label } from "~/components/ui/label"
import { cn } from "~/lib/utils";
import type { ClassificationServerResponse } from "~/types/classification";
import ListClassificationsApi from "~/api/classification/list-classifications-api";

interface ClassificationsSelectorProps {
  value: string | null
  handleChange: (value: string) => void
  classificationsError?: boolean
  isFilter?: boolean
  className?: string
}

const ClassificationsSelector = ({ 
  value, 
  handleChange, 
  classificationsError = false, 
  isFilter = false, 
  className 
}: ClassificationsSelectorProps) => {
  // const sources = use(listSourceApi())
  const [ classifications, setClassification ] = useState<ClassificationServerResponse[]>([])

  useEffect(() => {
    ListClassificationsApi()
      .then(data => setClassification(data.results))
      .catch(e => console.error(e))
  }, [])

  return ( 
    <div className={cn("grid gap-2", className)}>
      {!isFilter && <Label htmlFor="fuente" className="required">
        Classificación
      </Label>}
      <Select value={value || undefined} onValueChange={handleChange}>
        <SelectTrigger id="fuente" className={`w-full ${classificationsError ? "border-red-500" : ""}`}>
          <SelectValue placeholder="Seleccione una clasificación" />
        </SelectTrigger>
        <SelectContent>
          {isFilter && <SelectItem value="all">Todas</SelectItem>}
          {classifications.map((classification) => (
            <SelectItem key={classification.id} value={classification.name}>
              {classification.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {classificationsError && <p className="text-sm text-red-500">La fuente es requerida</p>}
    </div>
  );
}
 
export default ClassificationsSelector;