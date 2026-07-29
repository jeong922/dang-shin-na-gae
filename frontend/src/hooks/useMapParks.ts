import { useQuery } from '@tanstack/react-query';
import { getMapParks } from '../api/parksMap';

export const useMapParks = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['parks', 'map'],
    queryFn: getMapParks,
  });

  return { parks: data, isLoading, error };
};
