import { ApiError } from '../errors/ApiError';

const API_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_URL) {
  throw new Error('VITE_API_BASE_URL이 설정되지 않았습니다.');
}

export const apiClient = async <T>(url: string): Promise<T> => {
  try {
    const response = await fetch(`${API_URL}${url}`);

    if (!response.ok) {
      const data = await response.json();

      throw new ApiError(response.status, data?.detail ?? '요청에 실패했습니다.');
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
