import type { ParkFilter, ParkListResponse } from '../types/park';
import { ApiError } from '../errors/ApiError';

const API_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_URL) {
  throw new Error('VITE_API_BASE_URL이 설정되지 않았습니다.');
}

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

  try {
    const response = await fetch(`${API_URL}/parks?${params}`);

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
