import { useQuery } from '@tanstack/react-query';
import { getPark } from '../api/park';
import type { ParkDetail } from '../types/park';

export const usePark = ({ id, enabled = true }: { id: number; enabled?: boolean }) => {
  const query = useQuery<ParkDetail, Error>({
    queryKey: ['park', id],
    queryFn: () => getPark({ id }),
    enabled: enabled && Number.isInteger(id) && id > 0,
  });

  return {
    park: query.data,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
    isRefetching: query.isRefetching,
  };
};
