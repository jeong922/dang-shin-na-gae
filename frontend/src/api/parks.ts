import type { ParkFilter, ParkListResponse } from '../types/park';
import { apiClient } from './client';

export const getParks = async ({
  page,
  pageSize = 20,
  keyword = '',
  filters,
}: {
  page: number;
  pageSize?: number;
  keyword?: string;
  filters?: ParkFilter;
}): Promise<ParkListResponse> => {
  if (page < 1) {
    throw new Error('page는 1 이상이어야 합니다.');
  }

  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });

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

  return apiClient<ParkListResponse>(`/parks?${params}`);
};
