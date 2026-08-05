import type { ParkMapResponse, ParkParams } from '../types/park';
import { ApiError } from '../errors/ApiError';

const API_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_URL) {
  throw new Error('VITE_API_BASE_URL이 설정되지 않았습니다.');
}

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

  try {
    const response = await fetch(`${API_URL}/parks/map?${params}`);

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
