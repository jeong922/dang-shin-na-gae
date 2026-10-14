import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes, useNavigate } from 'react-router';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { ParkCompareProvider } from '../contexts/ParkCompareContext';
import { useParkCompare } from '../hooks/useParkCompare';
import { ParkCard } from '../components/parkList/ParkCard';
import { ParkDetailContent } from '../components/map/ParkDetailContent';
import ParkComparePage from './ParkComparePage';
import type { ParkDetail, ParkMap } from '../types/park';
import { getPark } from '../api/park';

vi.mock('../api/park', () => ({ getPark: vi.fn() }));
const parks: ParkMap[] = [1, 2, 3, 4].map((id) => ({
  id,
  name: `공원 ${id}`,
  lat: 37.5,
  lon: 127,
  district: '강남구',
  area: id * 100,
  difficulty: 'easy',
  avgSlope: id / 100,
  elevationDiff: id * 10,
  petStatus: 'restricted',
  petRestrictedLocations: ['온실'],
  serviceAnimalAllowed: false,
}));
const detail = (id: number): ParkDetail => ({
  id,
  name: `공원 ${id}`,
  description: '',
  location: { lat: 37.5, lon: 127, district: '강남구', address: '' },
  information: { area: id * 100, openedAt: '', facilities: [], plants: [] },
  difficulty: { level: 'easy', avgSlope: id / 100, elevationDiff: id * 10 },
  pet: {
    status: 'restricted',
    notices: ['목줄을 착용해주세요.'],
    restrictedLocations: ['온실'],
    serviceAnimalAllowed: false,
  },
  notices: [],
  directions: [],
  contact: { department: '', phone: '', url: '' },
  images: { image: '', map: '' },
});
const Selection = () => {
  const { ids } = useParkCompare();
  const navigate = useNavigate();
  return (
    <>
      <output data-testid='ids'>{ids.join(',')}</output>
      {parks.map((park) => (
        <ParkCard key={park.id} park={park} />
      ))}
      <button onClick={() => navigate('/sheet')}>시트로</button>
      <button onClick={() => navigate('/compare')}>비교 목록으로</button>
    </>
  );
};
let container: HTMLDivElement;
let root: Root;
let client: QueryClient;
const click = async (label: string) => {
  const button = Array.from(container.querySelectorAll('button')).find(
    (node) =>
      node.getAttribute('aria-label') === label || node.textContent === label,
  );
  expect(button, label).toBeDefined();
  await act(async () => {
    button!.click();
  });
};
const settle = async () => {
  await act(async () => {
    await new Promise((resolve) => setTimeout(resolve, 30));
  });
};

beforeEach(async () => {
  vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true);
  vi.mocked(getPark).mockImplementation(async ({ id }) => detail(id));
  container = document.createElement('div');
  document.body.append(container);
  root = createRoot(container);
  client = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });
  await act(async () =>
    root.render(
      <QueryClientProvider client={client}>
        <MemoryRouter>
          <ParkCompareProvider>
            <Routes>
              <Route path='/' element={<Selection />} />
              <Route
                path='/sheet'
                element={
                  <>
                    <ParkDetailContent park={parks[0]} />
                    <Selection />
                  </>
                }
              />
              <Route path='/compare' element={<ParkComparePage />} />
              <Route path='/parks/:id' element={<p>상세 페이지로 이동됨</p>} />
            </Routes>
          </ParkCompareProvider>
        </MemoryRouter>
      </QueryClientProvider>,
    ),
  );
});
afterEach(() => {
  act(() => root.unmount());
  client.clear();
  container.remove();
  vi.clearAllMocks();
  vi.unstubAllGlobals();
});

it('limits selection to three IDs and keeps comparison actions separate from card navigation', async () => {
  for (const id of [1, 2, 3, 4]) await click(`공원 ${id} 비교에 담기`);
  expect(container.querySelector('output')?.textContent).toBe('1,2,3');
  expect(container.textContent).toContain('최대 3개');
  expect(container.textContent).not.toContain('상세 페이지로 이동됨');
  expect(
    container
      .querySelector('[aria-label="공원 1 비교에서 빼기"]')
      ?.getAttribute('aria-pressed'),
  ).toBe('true');
  await click('공원 2 비교에서 빼기');
  await click('공원 4 비교에 담기');
  expect(container.querySelector('output')?.textContent).toBe('1,3,4');
});

it('shares selection between list and map sheet and survives navigation', async () => {
  await click('공원 1 비교에 담기');
  await click('시트로');
  expect(
    container.querySelectorAll('[aria-label="공원 1 비교에서 빼기"]'),
  ).toHaveLength(2);
  await click('공원 1 비교에서 빼기');
  expect(container.querySelector('output')?.textContent).toBe('');
  await click('공원 2 비교에 담기');
  await click('비교 목록으로');
  await settle();
  expect(container.textContent).toContain('공원 2');
  expect(container.textContent).toContain('공원을 1개 더');
  expect(container.querySelector('table')).toBeNull();
});

it('shows the empty selection and disables comparison', async () => {
  await click('비교 목록으로');
  expect(container.textContent).toContain('아직 담은 공원이 없어요');
  expect(container.querySelector('button')?.disabled).toBe(true);
});

it('does not restore a removed park when its pending request completes', async () => {
  let resolvePark!: (park: ParkDetail) => void;
  vi.mocked(getPark).mockImplementation(({ id }) =>
    id === 1
      ? new Promise<ParkDetail>((resolve) => {
          resolvePark = resolve;
        })
      : Promise.resolve(detail(id)),
  );
  await click('공원 1 비교에 담기');
  await click('공원 2 비교에 담기');
  await click('비교 목록으로');
  await settle();
  await click('공원 #1 비교에서 빼기');
  await act(async () => resolvePark(detail(1)));
  await settle();
  expect(container.textContent).toContain('공원 2');
  expect(container.textContent).not.toContain('공원 1');
  expect(container.textContent).toContain('공원을 1개 더');
});

it('renders a common-scale comparison and returns to the one-park state after removal', async () => {
  await click('공원 1 비교에 담기');
  await click('공원 2 비교에 담기');
  await click('비교 목록으로');
  await settle();
  await click('비교하기');
  expect(container.querySelectorAll('thead th')).toHaveLength(3);
  expect(container.textContent).toContain('100㎡');
  expect(container.textContent).toContain('200㎡');
  expect(container.textContent).toContain('1%');
  expect(container.textContent).toContain('온실');
  expect(container.textContent).toContain('실제 산책 코스 측정값이 아닙니다');
  expect(container.querySelector('[style="width: 50%;"]')).not.toBeNull();
  const cards = container.querySelector('[aria-label="공원별 비교 카드"]')!;
  expect(cards.querySelectorAll('article')).toHaveLength(2);
  expect(cards.querySelectorAll('dl')).toHaveLength(2);
  expect(cards.querySelector('div[aria-hidden="true"]')).toBeNull();
  expect(cards.textContent).toContain('온실');
  const summary = container.querySelector('[aria-label="비교 요약"]')!;
  expect(summary.textContent).toContain('공원 1 · 1%');
  expect(summary.textContent).toContain('공원 1 · 10m');
  await click('공원 1 비교에서 빼기');
  expect(container.querySelector('table')).toBeNull();
  expect(container.textContent).toContain('공원을 1개 더');
});

it('preserves a failed selection, displays other data, and retries the failed park', async () => {
  vi.mocked(getPark).mockImplementation(async ({ id }) => {
    if (id === 2) throw new Error('연결 실패');
    return detail(id);
  });
  await click('공원 1 비교에 담기');
  await click('공원 2 비교에 담기');
  await settle();
  await click('비교 목록으로');
  await settle();
  await click('비교하기');
  expect(container.textContent).toContain('100㎡');
  expect(container.textContent).toContain('정보를 불러오지 못했습니다');
  expect(container.querySelectorAll('thead th')).toHaveLength(3);
  expect(
    container.querySelector('[aria-label="비교 요약"]')?.textContent,
  ).toContain('모든 공원 정보를 불러오면');
  vi.mocked(getPark).mockImplementation(async ({ id }) => detail(id));
  await click('다시 시도');
  await settle();
  expect(container.textContent).toContain('200㎡');
  expect(container.querySelector('[role="alert"]')).toBeNull();
});

it('includes all tied parks in the summary', async () => {
  vi.mocked(getPark).mockImplementation(async ({ id }) => ({
    ...detail(id),
    difficulty: detail(1).difficulty,
  }));
  await click('공원 1 비교에 담기');
  await click('공원 2 비교에 담기');
  await click('비교 목록으로');
  await settle();
  await click('비교하기');
  expect(
    container.querySelector('[aria-label="비교 요약"]')?.textContent,
  ).toContain('공원 1, 공원 2 · 1% (공동 최저)');
});
