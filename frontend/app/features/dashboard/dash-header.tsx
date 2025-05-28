import { Button } from "~/components/ui/button";
import { RefreshCw, Filter } from "lucide-react";

const DashHeader = () => {
  return ( 
    <header className="sticky top-0 z-10 flex h-16 items-center gap-4 border-b bg-background">
      <div className='border-b'>
        <h1 className="text-3xl font-bold tracking-tight">Panel Principal.</h1>
        <p className="text-muted-foreground">Estadísticas y datos sobre las opiniones extraídas.</p>
      </div>
      <div className="ml-auto flex items-center gap-2">
        {/* <Button variant="outline" size="sm" className="h-8 gap-1">
          <RefreshCw className="h-3.5 w-3.5" />
          <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">Refrescar</span>
        </Button> */}
        {/* <Button variant="outline" size="sm" className="h-8 gap-1">
          <Filter className="h-3.5 w-3.5" />
          <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">Filtrar</span>
        </Button> */}
      </div>
    </header>
  );
}
 
export default DashHeader;