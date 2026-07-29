import { useQuery } from '@tanstack/react-query';
import { getMapParks } from '../api/parksMap';
import type { ParkMapResponse } from '../types/park';

export const useMapParks = () => {
  const { data, isLoading, error, refetch, isRefetching } = useQuery<ParkMapResponse>({
    queryKey: ['parks', 'map'],
    queryFn: getMapParks,
  });

  return {
    parks: data?.items ?? [],
    total: data?.total ?? 0,
    isLoading,
    error,
    refetch,
    isRefetching,
  };
};
