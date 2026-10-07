import { expect, it, vi } from 'vitest';
import { apiClient } from './client';
import { getParks } from './parks';

vi.mock('./client', () => ({ apiClient: vi.fn().mockResolvedValue({ items: [] }) }));

it('keeps pagination and search filters while applying a thirty-second timeout', async () => {
  await getParks({ page: 2, pageSize: 20, keyword: '공원', filters: { difficulty: ['easy'], district: ['강남구'] } });
  const [url, options] = vi.mocked(apiClient).mock.calls[0];
  const params = new URL(url, 'https://example.test').searchParams;
  expect(params.get('page')).toBe('2');
  expect(params.get('page_size')).toBe('20');
  expect(params.get('keyword')).toBe('공원');
  expect(params.get('difficulty')).toBe('easy');
  expect(params.get('district')).toBe('강남구');
  expect(options).toEqual({ timeoutMs: 30_000 });
});
