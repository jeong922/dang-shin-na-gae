import { useInfiniteQuery } from '@tanstack/react-query';
import { getParks } from '../api/parks';
import type { ParkFilter, ParkListResponse } from '../types/park';

interface Props {
  pageSize?: number;
  keyword?: string;
  filters?: ParkFilter;
}

export const useParks = ({ pageSize = 20, keyword = '', filters }: Props) => {
  const { data, isLoading, error, refetch, isRefetching, fetchNextPage, hasNextPage, isFetchingNextPage } =
    useInfiniteQuery<ParkListResponse, Error>({
      queryKey: ['parks', { pageSize, keyword, filters }],

      queryFn: ({ pageParam }) =>
        getParks({
          page: pageParam as number,
          pageSize,
          keyword,
          ...(filters ?? {}),
        }),

      initialPageParam: 1,

      getNextPageParam: (lastPage) => {
        if (lastPage.page >= lastPage.totalPages) {
          return undefined;
        }

        return lastPage.page + 1;
      },
    });

  const parks = data?.pages.flatMap((page) => page.items) ?? [];

  return {
    parks,
    total: data?.pages[0]?.total ?? 0,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error,
    refetch,
    isRefetching,
  };
};
