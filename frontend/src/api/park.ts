import type { ParkDetail } from '../types/park';
import { apiClient } from './client';

export const getPark = async ({ id }: { id: number }): Promise<ParkDetail> => {
  if (!Number.isInteger(id) || id <= 0) {
    throw new Error('올바르지 않은 공원 ID입니다.');
  }

  return apiClient<ParkDetail>(`/parks/${id}`);
};
