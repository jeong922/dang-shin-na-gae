import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { MemoryRouter } from 'react-router';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import type { Park } from '../../types/park';
import { ParkList } from './ParkList';

const state = vi.hoisted(() => ({
  parks: [] as Park[], total: 0, hasData: false, isLoading: true, isFetching: true,
  isFetchNextPageError: false, isFetchingNextPage: false, error: null as Error | null, hasNextPage: false,
  fetchNextPage: vi.fn(), refetch: vi.fn(),
}));
vi.mock('../../hooks/useParks', () => ({ useParks: () => state }));

let container: HTMLDivElement;
let root: Root;
const observe = vi.fn();
const park: Park = {
  id: 1, name: '테스트 공원', lat: 37.5, lon: 127, district: '강남구', area: 100,
  difficulty: 'easy', avgSlope: 1, elevationDiff: 2, petStatus: 'allowed',
};
const render = () => act(() => root.render(<MemoryRouter><ParkList /></MemoryRouter>));

beforeEach(() => {
  vi.useFakeTimers();
  vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true);
  vi.stubGlobal('IntersectionObserver', class {
    observe = observe;
    disconnect = vi.fn();
  });
  Object.assign(state, {
    parks: [], total: 0, hasData: false, isLoading: true, isFetching: true,
    isFetchNextPageError: false, isFetchingNextPage: false, error: null, hasNextPage: false,
  });
  vi.clearAllMocks();
  container = document.createElement('div');
  root = createRoot(container);
});
afterEach(() => {
  act(() => root.unmount());
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

it('only shows the server notice after five seconds and removes it on success', () => {
  render();
  const skeletonHeader = container.querySelector('header');
  expect(container.querySelector('[role="status"]')).toBeNull();
  act(() => vi.advanceTimersByTime(4_999));
  expect(container.querySelector('[role="status"]')).toBeNull();
  act(() => vi.advanceTimersByTime(1));
  expect(container.textContent).toContain('서버를 시작');
  const notice = container.querySelector<HTMLElement>('[role="status"]')!;
  expect(notice.classList.contains('fixed')).toBe(true);
  expect(notice.classList.contains('bottom-24')).toBe(true);
  expect(notice.classList.contains('left-1/2')).toBe(true);
  expect(container.querySelector('header')).toBe(skeletonHeader);
  Object.assign(state, { parks: [park], total: 1, hasData: true, isLoading: false, isFetching: false });
  render();
  expect(container.textContent).toContain(park.name);
  expect(container.querySelector('[role="status"]')).toBeNull();
});

it('immediately shows next-page loading and switches to the delayed notice after five seconds', () => {
  Object.assign(state, {
    parks: [park], total: 2, hasData: true, isLoading: false,
    hasNextPage: true, isFetchingNextPage: true,
  });
  render();
  expect(container.textContent).toContain('공원을 더 불러오는 중...');
  expect(container.textContent).not.toContain('응답이 지연');
  expect(container.textContent).toContain(park.name);
  act(() => vi.advanceTimersByTime(4_999));
  expect(container.textContent).toContain('공원을 더 불러오는 중...');
  act(() => vi.advanceTimersByTime(1));
  expect(container.textContent).toContain('응답이 지연');
  expect(container.textContent).not.toContain('공원을 더 불러오는 중...');
  Object.assign(state, { isFetching: false, isFetchingNextPage: false });
  render();
  expect(container.querySelector('[role="status"]')).toBeNull();
  expect(container.textContent).toContain(park.name);
});

it('offers retry after initial failure and suppresses the error during retry', () => {
  Object.assign(state, { isLoading: false, isFetching: false, error: new Error('응답 시간 초과') });
  render();
  expect(container.textContent).toContain('응답 시간 초과');
  act(() => container.querySelector<HTMLButtonElement>('[role="alert"] button')!.click());
  expect(state.refetch).toHaveBeenCalledOnce();
  state.isFetching = true;
  render();
  expect(container.querySelector('[role="alert"]')).toBeNull();
  expect(container.querySelector('[role="status"]')).toBeNull();
});

it('preserves loaded cards on next-page failure and retries the failed page manually', () => {
  Object.assign(state, {
    parks: [park], total: 2, hasData: true, isLoading: false, isFetching: false,
    hasNextPage: true, isFetchNextPageError: true, error: new Error('연결 실패'),
  });
  render();
  expect(container.textContent).toContain(park.name);
  expect(container.textContent).toContain('연결 실패');
  expect(observe).not.toHaveBeenCalled();
  act(() => container.querySelector<HTMLButtonElement>('[role="alert"] button')!.click());
  expect(state.fetchNextPage).toHaveBeenCalledOnce();
  expect(state.refetch).not.toHaveBeenCalled();
  state.isFetching = true;
  render();
  expect(container.textContent).toContain(park.name);
  expect(container.querySelector('[role="alert"]')).toBeNull();
  act(() => vi.advanceTimersByTime(5_000));
  expect(container.textContent).toContain('응답이 지연');
  Object.assign(state, { isFetching: false, error: null, isFetchNextPageError: false });
  render();
  expect(observe).toHaveBeenCalledOnce();
});
