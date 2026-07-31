import { useQuery } from '@tanstack/react-query';
import { getPark } from '../api/park';
import type { ParkDetail } from '../types/park';

export const usePark = ({ id }: { id: number }) => {
  const { data, isLoading, error, refetch, isRefetching } = useQuery<ParkDetail, Error>({
    queryKey: ['park', id],
    queryFn: () => getPark({ id }),
    enabled: !!id,
  });

  return {
    park: data,
    isLoading,
    error,
    refetch,
    isRefetching,
  };
};
