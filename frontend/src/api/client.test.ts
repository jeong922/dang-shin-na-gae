import { afterEach, beforeEach, expect, it, vi } from 'vitest';

beforeEach(() => {
  vi.useFakeTimers();
  vi.stubEnv('VITE_API_BASE_URL', 'https://example.test');
});
afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

it('aborts at thirty seconds and reports a timeout', async () => {
  vi.stubGlobal('fetch', vi.fn((_url: string, options: RequestInit) => new Promise((_resolve, reject) => {
    options.signal!.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
  })));
  const { apiClient } = await import('./client');
  const result = apiClient('/parks/map', { timeoutMs: 30_000 });
  const assertion = expect(result).rejects.toThrow('서버 응답 시간이 초과');
  await vi.advanceTimersByTimeAsync(29_999);
  expect(vi.getTimerCount()).toBe(1);
  await vi.advanceTimersByTimeAsync(1);
  await assertion;
  expect(vi.getTimerCount()).toBe(0);
});

it('clears the timeout after success and preserves HTTP errors', async () => {
  const fetchMock = vi.fn().mockResolvedValueOnce({ ok: true, json: async () => ({ items: [] }) })
    .mockResolvedValueOnce({ ok: false, status: 503, json: async () => ({ detail: 'Unavailable' }) });
  vi.stubGlobal('fetch', fetchMock);
  const { apiClient } = await import('./client');
  await expect(apiClient('/parks/map', { timeoutMs: 30_000 })).resolves.toEqual({ items: [] });
  expect(vi.getTimerCount()).toBe(0);
  await expect(apiClient('/parks/map', { timeoutMs: 30_000 })).rejects.toMatchObject({ status: 503, message: 'Unavailable' });
  expect(vi.getTimerCount()).toBe(0);
});

it('reports network failure and clears the timeout', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));
  const { apiClient } = await import('./client');
  await expect(apiClient('/parks/search', { timeoutMs: 30_000 })).rejects.toThrow('서버와 연결할 수 없습니다.');
  expect(vi.getTimerCount()).toBe(0);
});

it('does not add a timeout to callers without timeout options', async () => {
  const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ id: 1 }) });
  vi.stubGlobal('fetch', fetchMock);
  const { apiClient } = await import('./client');
  await expect(apiClient('/parks/1')).resolves.toEqual({ id: 1 });
  expect(fetchMock).toHaveBeenCalledWith('https://example.test/parks/1', undefined);
  expect(vi.getTimerCount()).toBe(0);
});
