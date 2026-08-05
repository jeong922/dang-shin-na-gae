import { useQuery } from '@tanstack/react-query';
import type { ParkParams, ParkMapResponse } from '../types/park';
import { getMapParks } from '../api/parksMap';

export const useMapParks = (params: ParkParams) => {
  const query = useQuery<ParkMapResponse, Error>({
    queryKey: [
      'parks-map',
      {
        west: params.west,
        south: params.south,
        east: params.east,
        north: params.north,
      },
    ],

    queryFn: () => getMapParks(params),

    enabled:
      params.west !== undefined &&
      params.south !== undefined &&
      params.east !== undefined &&
      params.north !== undefined,
    staleTime: 1000 * 60,
    gcTime: 1000 * 60 * 30,
    placeholderData: (previous) => previous,
  });

  return {
    parks: query.data?.items ?? [],
    total: query.data?.total ?? 0,
    isLoading: query.isLoading,
    isFetching: query.isFetching,
    error: query.error,
    refetch: query.refetch,
  };
};
