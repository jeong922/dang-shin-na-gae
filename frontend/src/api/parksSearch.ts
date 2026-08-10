import type { ParkFilter, ParkSearchResponse } from '../types/park';
import { apiClient } from './client';

export const searchParks = async ({
  keyword,
  filters,
}: {
  keyword: string;
  filters?: ParkFilter;
}): Promise<ParkSearchResponse> => {
  const params = new URLSearchParams();

  if (keyword) {
    params.set('keyword', keyword);
  }

  filters?.difficulty?.forEach((value) => {
    params.append('difficulty', value);
  });

  filters?.district?.forEach((value) => {
    params.append('district', value);
  });

  filters?.petStatus?.forEach((value) => {
    params.append('pet_status', value);
  });

  return apiClient<ParkSearchResponse>(`/parks/search?${params}`);
};
