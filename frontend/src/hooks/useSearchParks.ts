import { useQuery } from '@tanstack/react-query';
import type { ParkSearchResponse } from '../types/park';
import { searchParks } from '../api/parksSearch';

export const useSearchParks = ({ keyword }: { keyword: string }) => {
  const query = useQuery<ParkSearchResponse, Error>({
    queryKey: ['parks-search', keyword],
    queryFn: () =>
      searchParks({
        keyword,
      }),
    enabled: !!keyword?.trim(),
    staleTime: 1000 * 60,
  });

  return {
    parks: query.data?.items ?? [],
    total: query.data?.total ?? 0,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  };
};
