import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select"
import { use, useEffect, useState } from "react";
import listSourceApi from "~/api/source/list-souce-api";
import { Label } from "~/components/ui/label"
import type { Source } from "~/types/comments";

interface SourceSelectorProps {
  value: string
  handleChange: (value: string) => void
  sourceError: boolean
}

const SourceSelector = ({ value, handleChange, sourceError }: SourceSelectorProps) => {
  // const sources = use(listSourceApi())
  const [ sources, setSources ] = useState<Source[]>([])

  useEffect(() => {
    listSourceApi()
      .then(data => setSources(data.results))
      .catch(e => console.error(e))
  }, [])

  console.log({sources});
  

  return ( 
    <div className="grid gap-2">
      <Label htmlFor="fuente" className="required">
        Fuente
      </Label>
      <Select value={value} onValueChange={handleChange}>
        <SelectTrigger id="fuente" className={sourceError ? "border-red-500" : ""}>
          <SelectValue placeholder="Seleccione una fuente" />
        </SelectTrigger>
        <SelectContent>
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