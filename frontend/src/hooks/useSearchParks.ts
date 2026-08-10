import { useQuery } from '@tanstack/react-query';
import type { ParkFilter, ParkSearchResponse } from '../types/park';
import { searchParks } from '../api/parksSearch';

interface Props {
  keyword?: string;
  filters?: ParkFilter;
}

export const useSearchParks = ({ keyword = '', filters }: Props) => {
  const hasSearchCondition = !!keyword.trim() || Object.values(filters ?? {}).some((values) => values?.length > 0);

  const query = useQuery<ParkSearchResponse, Error>({
    queryKey: ['parks-search', { keyword, filters }],
    queryFn: () =>
      searchParks({
        keyword,
        filters,
      }),
    enabled: hasSearchCondition,
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
