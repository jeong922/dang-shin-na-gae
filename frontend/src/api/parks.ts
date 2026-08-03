import type { ParkListResponse } from '../types/park';

const API_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_URL) {
  throw new Error('VITE_API_BASE_URL이 설정되지 않았습니다.');
}

export const getParks = async ({
  page,
  pageSize = 20,
  keyword = '',
  difficulty,
  district,
  petStatus,
}: {
  page: number;
  pageSize?: number;
  keyword?: string;
  difficulty?: string;
  district?: string;
  petStatus?: string;
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

  if (difficulty) {
    params.set('difficulty', difficulty);
  }

  if (district) {
    params.set('district', district);
  }

  if (petStatus) {
    params.set('pet_status', petStatus);
  }

  try {
    const response = await fetch(`${API_URL}/parks?${params}`);

    if (!response.ok) {
      throw new Error('공원 데이터를 가져오는데 실패했습니다.');
    }

    return await response.json();
  } catch {
    throw new Error('서버와 연결할 수 없습니다.');
  }
};
