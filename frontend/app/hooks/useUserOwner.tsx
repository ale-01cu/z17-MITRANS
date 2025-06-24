import listUserOwnerApi from "~/api/user-owner/list-user-owner-api"
import { useQuery } from "@tanstack/react-query"

export default function useUserOwner(currentPage: number, searchTerm: string) {
  const { data, status } = useQuery({
    queryKey: ['user-owner', searchTerm], 
    refetchInterval: 5000,
    staleTime: 5000,
    gcTime: 3000,
    queryFn: async () => await listUserOwnerApi(100, currentPage, searchTerm)}
  )

  return {
    data,
    isFetching: status === 'pending'
  }
}