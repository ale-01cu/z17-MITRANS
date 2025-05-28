import { Card, CardContent } from "~/components/ui/card";
import { Input } from "~/components/ui/input";
import { Search } from "lucide-react";

interface UsersSearchAndFiltersProps {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
}

export default function UsersSearchAndFilters({ 
  searchTerm, 
  setSearchTerm, 
}: UsersSearchAndFiltersProps) {
  return (
    <Card>
      <CardContent>
        <div className="flex flex-col space-y-4 md:flex-row md:items-center md:space-y-0 md:space-x-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search users by name, email, department, or role..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}