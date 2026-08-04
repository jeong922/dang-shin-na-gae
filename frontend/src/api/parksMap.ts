import type { ParkMapResponse, MapParkParams } from '../types/park';

const API_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_URL) {
  throw new Error('VITE_API_BASE_URL이 설정되지 않았습니다.');
}

export const getMapParks = async ({ filters, keyword, ...bounds }: MapParkParams): Promise<ParkMapResponse> => {
  const params = new URLSearchParams();

  if (bounds.west !== undefined) params.set('west', String(bounds.west));
  if (bounds.south !== undefined) params.set('south', String(bounds.south));
  if (bounds.east !== undefined) params.set('east', String(bounds.east));
  if (bounds.north !== undefined) params.set('north', String(bounds.north));

  if (keyword) {
    params.set('keyword', keyword);
  }

  if (filters?.difficulty) {
    params.set('difficulty', filters.difficulty);
  }

  if (filters?.district) {
    params.set('district', filters.district);
  }

  if (filters?.petStatus) {
    params.set('pet_status', filters.petStatus);
  }

  const response = await fetch(`${API_URL}/parks/map?${params}`);

  if (!response.ok) {
    throw new Error('공원 데이터를 가져오는데 실패했습니다.');
  }

  return response.json();
};
