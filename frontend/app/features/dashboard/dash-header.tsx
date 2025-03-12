import { Button } from "~/components/ui/button";
import { RefreshCw, Filter } from "lucide-react";

const DashHeader = () => {
  return ( 
    <header className="sticky top-0 z-10 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
      <h1 className="text-lg font-semibold md:text-2xl">Opinion Dashboard</h1>
      <div className="ml-auto flex items-center gap-2">
        <Button variant="outline" size="sm" className="h-8 gap-1">
          <RefreshCw className="h-3.5 w-3.5" />
          <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">Refresh Data</span>
        </Button>
        <Button variant="outline" size="sm" className="h-8 gap-1">
          <Filter className="h-3.5 w-3.5" />
          <span className="sr-only sm:not-sr-only sm:whitespace-nowrap">Filter</span>
        </Button>
      </div>
    </header>
  );
}
 
export default DashHeader;