import { useState, type ReactNode } from 'react';
import { useQueries } from '@tanstack/react-query';
import { Link } from 'react-router';
import { X } from 'lucide-react';
import { getPark } from '../api/park';
import { useParkCompare } from '../hooks/useParkCompare';
import type { ParkDetail } from '../types/park';
import { Button } from '../components/ui/Button';
import { DifficultyBadge } from '../components/park/DifficultyBadge';
import { PetStatusBadge } from '../components/park/PetStatusBadge';
import { DIFFICULTY_OPTIONS } from '../constants/difficulty';
import { PET_STATUS_OPTIONS } from '../constants/petStatus';
import { formatMeter, formatPercent } from '../utils/format';

const metrics = [
  {
    label: '면적',
    value: (park: ParkDetail) => park.information.area,
    format: (value: number) => `${new Intl.NumberFormat('ko-KR', { maximumFractionDigits: 2 }).format(value)}㎡`,
  },
  {
    label: '평균 경사도 (추정)',
    value: (park: ParkDetail) => park.difficulty.avgSlope,
    format: formatPercent,
  },
  {
    label: '고도 차이 (추정)',
    value: (park: ParkDetail) => park.difficulty.elevationDiff,
    format: (value: number) => `${formatMeter(value)}m`,
  },
];

const PetNotices = ({ park }: { park: ParkDetail }) => (
  <div className='space-y-3 leading-6'>
    {park.pet.restrictedLocations.length > 0 && <p>제한 장소: {park.pet.restrictedLocations.join(', ')}</p>}
    {park.pet.notices.length > 0 && (
      <ul className='list-disc pl-4'>
        {park.pet.notices.map((notice, index) => (
          <li key={index}>{notice}</li>
        ))}
      </ul>
    )}
    {park.pet.serviceAnimalAllowed && <p>안내견은 제한 구역에서도 출입 가능합니다.</p>}
    {park.pet.restrictedLocations.length === 0 && park.pet.notices.length === 0 && (
      <p className='text-text-muted'>추가 안내 정보가 없습니다.</p>
    )}
  </div>
);

const ParkComparePage = () => {
  const { ids, toggle } = useParkCompare();
  const [showComparison, setShowComparison] = useState(false);
  const queries = useQueries({
    queries: ids.map((id) => ({
      queryKey: ['park', id],
      queryFn: () => getPark({ id }),
    })),
  });
  const comparing = showComparison && ids.length >= 2;
  const parks = queries.flatMap((query) => (query.data ? [query.data] : []));
  const summaryReady =
    parks.length === ids.length &&
    queries.every((query) => !query.isError && !query.isFetching) &&
    parks.every((park) => Number.isFinite(park.difficulty.avgSlope) && Number.isFinite(park.difficulty.elevationDiff));

  const cells = (render: (park: ParkDetail) => ReactNode) =>
    queries.map((query, index) => (
      <td key={ids[index]} className='border-b border-border p-3 align-top md:p-4'>
        {query.data ? render(query.data) : <span className='text-text-muted'>—</span>}
      </td>
    ));

  return (
    <section className='min-w-0 space-y-5 px-page py-6 sm:py-8 wrap-anywhere'>
      <header>
        <h1 className='text-display font-semibold'>공원 비교하기</h1>
        <p className='mt-2 text-sm text-text-secondary'>
          관심 있는 공원 2~3개의 정보를 나란히 확인하세요. ({ids.length}/3)
        </p>
      </header>
      <div className='flex flex-wrap items-center gap-4 text-sm'>
        <Link to='/' className='text-brand underline'>
          지도에서 담기
        </Link>
        <Link to='/parks' className='text-brand underline'>
          공원 목록에서 담기
        </Link>
      </div>
      {ids.length < 2 && (
        <p className='rounded-card border border-border bg-surface p-4' role='status'>
          {ids.length === 0
            ? '아직 담은 공원이 없어요. 지도나 목록에서 비교할 공원을 담아주세요.'
            : '공원을 1개 더 담으면 비교할 수 있어요.'}
        </p>
      )}
      {!comparing && ids.length > 0 && (
        <ul className='space-y-3'>
          {ids.map((id, index) => (
            <li
              key={id}
              className='flex flex-wrap items-center justify-between gap-3 rounded-card border border-border bg-surface p-4'
            >
              <span className='min-w-0 flex-1'>{queries[index].data?.name ?? `공원 #${id}`}</span>
              <Button
                variant='secondary'
                aria-label={`${queries[index].data?.name ?? `공원 #${id}`} 비교에서 빼기`}
                onClick={() => toggle(id, queries[index].data?.name ?? `공원 #${id}`)}
              >
                제거
              </Button>
            </li>
          ))}
        </ul>
      )}
      {!comparing && (
        <Button disabled={ids.length < 2} onClick={() => setShowComparison(true)}>
          비교하기
        </Button>
      )}

      {/* 한 공원의 조회 실패가 다른 공원의 비교를 막지 않는다. */}
      {queries.map((query, index) =>
        query.isPending || query.isError ? (
          <div
            key={ids[index]}
            role={query.isError ? 'alert' : 'status'}
            className='rounded-card border border-border bg-surface p-4 text-sm'
          >
            {query.isError
              ? `${query.data?.name ?? `공원 #${ids[index]}`} 정보를 불러오지 못했습니다.`
              : `공원 #${ids[index]} 정보를 불러오는 중입니다.`}
            {query.isError && (
              <Button
                variant='secondary'
                className='ml-3'
                onClick={() => {
                  void query.refetch();
                }}
              >
                다시 시도
              </Button>
            )}
          </div>
        ) : null,
      )}

      {comparing && (
        <>
          <p className='text-sm leading-6 text-text-secondary md:hidden'>
            경사·고도 차이는 주변 표본 기반 추정치입니다. 방문 전 반려견 출입 안내를 확인하세요. 막대는 상대 크기이며
            우열을 뜻하지 않습니다.
          </p>
          <p id='compare-note' className='hidden text-sm leading-6 text-text-secondary md:block'>
            평균 경사도와 고도 차이는 공원 주변 표본의 고도로 계산한 추정치이며 실제 산책 코스 측정값이 아닙니다. 막대는
            현재 선택한 공원 사이의 항목별 상대 크기이며, 길이가 좋고 나쁨을 뜻하지 않습니다. 출입 안내는 방문 전 공식
            홈페이지에서 확인해주세요.
          </p>
          <section
            aria-label='비교 요약'
            className='space-y-2 rounded-card border border-border bg-surface p-4 text-sm leading-6'
          >
            <h2 className='font-semibold'>선택한 공원 비교 요약</h2>
            {summaryReady ? (
              metrics.slice(1).map((metric) => {
                const minimum = Math.min(...parks.map(metric.value));
                const names = parks.filter((park) => metric.value(park) === minimum).map((park) => park.name);
                return (
                  <p key={metric.label}>
                    {metric.label}: <span className='font-medium'>{names.join(', ')}</span> · {metric.format(minimum)}
                    {names.length > 1 ? ' (공동 최저)' : ' (가장 낮음)'}
                  </p>
                );
              })
            ) : (
              <p className='text-text-muted'>
                모든 공원 정보를 불러오면 요약을 표시합니다. 조회 오류가 있으면 다시 시도해주세요.
              </p>
            )}
            <p className='text-text-muted'>선택한 공원 간 수치 비교이며 종합적인 우열을 뜻하지 않습니다.</p>
          </section>
          <p id='compare-scroll-hint' className='text-sm text-text-muted md:hidden'>
            ← 좌우로 밀어 공원을 비교하세요. 비교 항목은 왼쪽에 고정됩니다. →
          </p>
          <div
            role='region'
            aria-label='공원 비교 표, 좁은 화면에서 좌우로 스크롤할 수 있습니다'
            aria-describedby='compare-scroll-hint'
            tabIndex={0}
            className='max-w-full overflow-x-auto overscroll-x-contain rounded-card border border-border bg-surface'
          >
            <table
              aria-describedby='compare-note'
              className={`w-full table-fixed text-sm ${ids.length === 2 ? 'min-w-110 md:min-w-130' : 'min-w-154 md:min-w-180'}`}
            >
              <caption className='sr-only'>선택한 공원의 면적, 지형 추정치, 난이도 및 반려견 이용 안내 비교</caption>
              <thead>
                <tr>
                  <th
                    scope='col'
                    className='sticky left-0 z-10 w-22 border-b border-border bg-slate-50 p-3 text-left md:w-30 md:p-4'
                  >
                    비교 항목
                  </th>
                  {ids.map((id, index) => (
                    <th scope='col' key={id} className='border-b border-border p-3 text-left align-top md:p-4'>
                      <div className='flex items-start gap-2'>
                        <Link
                          to={`/parks/${id}`}
                          className='min-w-0 flex-1 pt-2 text-base font-semibold underline md:text-title'
                        >
                          {queries[index].data?.name ?? `공원 #${id}`}
                        </Link>
                        <button
                          type='button'
                          className='inline-flex size-11 shrink-0 items-center justify-center rounded-full text-text-muted transition-colors hover:bg-slate-50 hover:text-text-primary'
                          aria-label={`${queries[index].data?.name ?? `공원 #${id}`} 비교에서 빼기`}
                          title='비교에서 빼기'
                          onClick={() => toggle(id, queries[index].data?.name ?? `공원 #${id}`)}
                        >
                          <X size={18} aria-hidden='true' />
                        </button>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {metrics.map((metric) => {
                  const maximum = Math.max(
                    0,
                    ...queries.flatMap((query) => (query.data ? [metric.value(query.data)] : [])),
                  );
                  return (
                    <tr key={metric.label}>
                      <th
                        scope='row'
                        className='sticky left-0 z-10 border-b border-border bg-slate-50 p-3 text-left md:p-4'
                      >
                        {metric.label}
                      </th>
                      {cells((park) => (
                        <>
                          <span className='tabular-nums'>{metric.format(metric.value(park))}</span>
                          <div aria-hidden='true' className='mt-3 h-2 rounded-full bg-slate-100'>
                            <div
                              className='h-full rounded-full bg-slate-500'
                              style={{
                                width: `${maximum > 0 ? (metric.value(park) / maximum) * 100 : 0}%`,
                              }}
                            />
                          </div>
                        </>
                      ))}
                    </tr>
                  );
                })}
                <tr>
                  <th
                    scope='row'
                    className='sticky left-0 z-10 border-b border-border bg-slate-50 p-3 text-left md:p-4'
                  >
                    난이도
                  </th>
                  {cells((park) => (
                    <DifficultyBadge difficulty={DIFFICULTY_OPTIONS[park.difficulty.level]} />
                  ))}
                </tr>
                <tr>
                  <th
                    scope='row'
                    className='sticky left-0 z-10 border-b border-border bg-slate-50 p-3 text-left md:p-4'
                  >
                    반려견 이용
                  </th>
                  {cells((park) => (
                    <PetStatusBadge status={PET_STATUS_OPTIONS[park.pet.status]} />
                  ))}
                </tr>
                <tr>
                  <th
                    scope='row'
                    className='sticky left-0 z-10 border-b border-border bg-slate-50 p-3 text-left md:p-4'
                  >
                    이용·제한 안내
                  </th>
                  {cells((park) => (
                    <PetNotices park={park} />
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
};

export default ParkComparePage;
