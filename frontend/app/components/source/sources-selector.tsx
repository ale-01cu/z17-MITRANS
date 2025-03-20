import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select"
import { use, useEffect, useState } from "react";
import listSourceApi from "~/api/source/list-souce-api";
import { Label } from "~/components/ui/label"
import type { Source } from "~/types/source";
import { cn } from "~/lib/utils";

interface SourceSelectorProps {
  value: string
  handleChange: (value: string) => void
  sourceError?: boolean
  isFilter?: boolean
  className?: string
}

const SourceSelector = ({ 
  value, handleChange, sourceError = false, isFilter = false, className }: SourceSelectorProps) => {
  // const sources = use(listSourceApi())
  const [ sources, setSources ] = useState<Source[]>([])

  useEffect(() => {
    listSourceApi()
      .then(data => setSources(data.results))
      .catch(e => console.error(e))
  }, [])


  return ( 
    <div className={cn("grid gap-2", className)}>
      {!isFilter && <Label htmlFor="fuente" className="required">
        Fuente
      </Label>}
      <Select value={value} onValueChange={handleChange}>
        <SelectTrigger id="fuente" className={`w-full ${sourceError ? "border-red-500" : ""}`}>
          <SelectValue placeholder="Seleccione una fuente" />
        </SelectTrigger>
        <SelectContent>
          {isFilter && <SelectItem value="all">Todas las fuentes</SelectItem>}
          {sources.map((source) => (
            <SelectItem key={source.id} value={source.id}>
              {source.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {sourceError && <p className="text-sm text-red-500">La fuente es requerida</p>}
    </div>
  );
}
 
export default SourceSelector;