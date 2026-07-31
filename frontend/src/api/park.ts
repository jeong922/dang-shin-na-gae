import type { ParkDetail } from '../types/park';

const API_URL = import.meta.env.VITE_API_BASE_URL;

export const getPark = async ({ id }: { id: number }): Promise<ParkDetail> => {
  if (!id) {
    throw new Error('id 값이 필요합니다.');
  }

  try {
    const response = await fetch(`${API_URL}/parks/${id}`);

    if (!response.ok) {
      throw new Error('공원 데이터를 가져오는데 실패했습니다.');
    }

    return await response.json();
  } catch {
    throw new Error('서버와 연결할 수 없습니다.');
  }
};
