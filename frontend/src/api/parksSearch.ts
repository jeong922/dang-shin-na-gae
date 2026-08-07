import type { ParkSearchResponse } from '../types/park';
import { apiClient } from './client';

export const searchParks = async ({ keyword }: { keyword: string }): Promise<ParkSearchResponse> => {
  const params = new URLSearchParams();

  if (keyword) {
    params.set('keyword', keyword);
  }

  return apiClient<ParkSearchResponse>(`/parks/search?${params}`);
};
