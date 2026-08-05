import type { ParkDetail } from '../types/park';
import { ApiError } from '../errors/ApiError';

const API_URL = import.meta.env.VITE_API_BASE_URL;

export const getPark = async ({ id }: { id: number }): Promise<ParkDetail> => {
  if (!Number.isInteger(id) || id <= 0) {
    throw new Error('올바르지 않은 공원 ID입니다.');
  }

  try {
    const response = await fetch(`${API_URL}/parks/${id}`);

    if (!response.ok) {
      const data = await response.json();

      throw new ApiError(response.status, data.detail ?? '공원 데이터를 가져오는데 실패했습니다.');
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    throw new Error('서버와 연결할 수 없습니다.', {
      cause: error,
    });
  }
};
