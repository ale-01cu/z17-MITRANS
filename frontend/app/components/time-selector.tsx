import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "~/components/ui/select"
import { Label } from "~/components/ui/label"
import { cn } from "~/lib/utils";

interface TimeSelectorProps {
  value: string | undefined
  handleChange: (value: string) => void
  classificationsError?: boolean
  isFilter?: boolean
  className?: string
}

const HOURS = [
  { label: '24 Horas', hours: '24' },
  { label: '48 Horas', hours: '48' },
  { label: '72 Horas', hours: '72' },
  { label: '1 Semana', hours: '168' },
  { label: '1 Mes', hours: '720' },
]

const TimeSelector = ({ 
  value, 
  handleChange, 
  classificationsError = false, 
  isFilter = false, 
  className 
}: TimeSelectorProps) => {
  // const sources = use(listSourceApi())

  return ( 
    <div className={cn("grid gap-2", className)}>
      {!isFilter && <Label htmlFor="fuente" className="required">
        Tiempo
      </Label>}
      <Select value={value || undefined} onValueChange={handleChange}>
        <SelectTrigger id="fuente" className={`w-full ${classificationsError ? "border-red-500" : ""}`}>
          <SelectValue placeholder="Tiempo" />
        </SelectTrigger>
        <SelectContent>
          {isFilter && <SelectItem value="all">Todas</SelectItem>}
          {HOURS.map((hour) => (
            <SelectItem key={hour.label} value={hour.hours}>
              Hace {hour.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {classificationsError && <p className="text-sm text-red-500">La fuente es requerida</p>}
    </div>
  );
}
 
export default TimeSelector;