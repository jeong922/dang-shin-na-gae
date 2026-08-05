import type { ParkMapResponse, ParkParams } from '../types/park';
import { apiClient } from './client';

export const getMapParks = async ({ filters, keyword, ...bounds }: ParkParams): Promise<ParkMapResponse> => {
  const params = new URLSearchParams();

  if (bounds.west !== undefined) params.set('west', String(bounds.west));
  if (bounds.south !== undefined) params.set('south', String(bounds.south));
  if (bounds.east !== undefined) params.set('east', String(bounds.east));
  if (bounds.north !== undefined) params.set('north', String(bounds.north));

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

  return apiClient<ParkMapResponse>(`/parks/map?${params}`);
};
