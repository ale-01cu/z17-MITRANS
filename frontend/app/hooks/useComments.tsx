import { useQuery } from "@tanstack/react-query"
import listCommentsApi from "~/api/comments/list-comments-api"

export default function useComments(currentPage: number) {
  const { data, status } = useQuery({
    queryKey: ['comments'], 
    refetchInterval: 5000,
    staleTime: 5000,
    gcTime: 3000,
    queryFn: async () => await listCommentsApi({ page: currentPage })}
  )

  return {
    data,
    isFetching: status === 'pending'
  }
}