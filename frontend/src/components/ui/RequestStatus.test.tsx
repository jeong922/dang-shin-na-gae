import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { RequestStatus, type RequestState } from './RequestStatus';

let container: HTMLDivElement;
let root: Root;
const refetch = vi.fn();
const render = (state: Partial<RequestState> = {}, key = 'request') => act(() => {
  root.render(<RequestStatus key={key} isFetching hasData={false} error={null} refetch={refetch} {...state} />);
});

beforeEach(() => {
  vi.useFakeTimers();
  vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true);
  container = document.createElement('div');
  root = createRoot(container);
  refetch.mockClear();
});
afterEach(() => {
  act(() => root.unmount());
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

it('shows nothing before five seconds and shows the delayed notice at five seconds', () => {
  render();
  act(() => vi.advanceTimersByTime(4_999));
  expect(container.textContent).toBe('');
  act(() => vi.advanceTimersByTime(1));
  expect(container.textContent).toContain('서버를 시작');
  render({ isFetching: false });
  expect(container.textContent).toBe('');
});

it('resets the delay on a new request and distinguishes existing data', () => {
  render();
  act(() => vi.advanceTimersByTime(4_000));
  render({ hasData: true }, 'new-request');
  act(() => vi.advanceTimersByTime(4_999));
  expect(container.textContent).toBe('');
  act(() => vi.advanceTimersByTime(1));
  expect(container.textContent).toContain('응답이 지연');
});

it('offers retry on failure and hides the error and retry button while retrying', () => {
  const error = new Error('연결 실패');
  render({ isFetching: false, error }, 'failed');
  expect(container.textContent).toContain('연결 실패');
  act(() => container.querySelector('button')!.click());
  expect(refetch).toHaveBeenCalledOnce();
  render({ error }, 'retrying');
  expect(container.textContent).toBe('');
  expect(container.querySelector('button')).toBeNull();
});

it('cleans up the delay timer when unmounted', () => {
  render();
  act(() => root.render(null));
  expect(vi.getTimerCount()).toBe(0);
});
