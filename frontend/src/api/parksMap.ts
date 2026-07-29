import type { ParkMapResponse } from '../types/park';

const API_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_URL) {
  throw new Error('VITE_API_BASE_URL이 설정되지 않았습니다.');
}

export const getMapParks = async (): Promise<ParkMapResponse> => {
  try {
    const response = await fetch(`${API_URL}/parks/map`);

    if (!response.ok) {
      throw new Error('공원 데이터를 가져오는데 실패했습니다.');
    }

    return await response.json();
  } catch {
    throw new Error('서버와 연결할 수 없습니다.');
  }
};
