import { ApiError } from '../errors/ApiError';

const API_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_URL) {
  throw new Error('VITE_API_BASE_URL이 설정되지 않았습니다.');
}

export const apiClient = async <T>(url: string, options: { timeoutMs?: number } = {}): Promise<T> => {
  const controller = options.timeoutMs === undefined ? undefined : new AbortController();
  const timer = controller ? setTimeout(() => controller.abort(), options.timeoutMs) : undefined;
  try {
    const response = await fetch(`${API_URL}${url}`, controller ? { signal: controller.signal } : undefined);

    if (!response.ok) {
      const data = await response.json();

      throw new ApiError(response.status, data?.detail ?? '요청에 실패했습니다.');
    }

    return await response.json();
  } catch (error) {
    if (controller?.signal.aborted) {
      throw new Error('서버 응답 시간이 초과되었습니다. 다시 시도해주세요.', { cause: error });
    }
    if (error instanceof ApiError) {
      throw error;
    }

    throw new Error('서버와 연결할 수 없습니다.', {
      cause: error,
    });
  } finally {
    clearTimeout(timer);
  }
};
