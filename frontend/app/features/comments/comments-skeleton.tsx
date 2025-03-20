import { Skeleton } from "~/components/ui/skeleton"

const CommentsSkeleton = () => {
  return ( 
    <div className="space-y-4">
      <div className="flex flex-col space-y-3">
        <Skeleton className="h-10 w-full" />
        <div className="flex space-x-2">
          <Skeleton className="h-10 w-1/3" />
          <Skeleton className="h-10 w-1/3" />
          <Skeleton className="h-10 w-1/3" />
        </div>
      </div>
      <Skeleton className="h-[400px] w-full rounded-md" />
    </div>
   );
}
 
export default CommentsSkeleton;