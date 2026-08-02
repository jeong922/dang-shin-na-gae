import { useEffect, useRef } from 'react';
import { ParkCard } from './ParkCard';
import { useParks } from '../../hooks/useParks';
import { ErrorOverlay } from '../common/ErrorOverlay';
import { ParkListSkeleton } from './ParkListSkeleton';

export const ParkList = () => {
  const { parks, total, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading, error, refetch } = useParks({
    pageSize: 20,
  });

  const observerTarget = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!observerTarget.current) return;
    if (!hasNextPage) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      {
        threshold: 1,
      },
    );

    observer.observe(observerTarget.current);

    return () => {
      observer.disconnect();
    };
  }, [fetchNextPage, hasNextPage, isFetchingNextPage]);

  if (isLoading) {
    return <ParkListSkeleton />;
  }

  if (error) {
    return <ErrorOverlay onRetry={refetch} />;
  }

  return (
    <section className='mx-auto my-6 max-w-5xl space-y-6 px-6'>
      <header>
        <h1 className='text-3xl font-bold'>공원 목록</h1>

        <p className='mt-1 text-text-muted'>
          총 <span className='font-semibold text-brand'>{total}</span>
          개의 공원
        </p>
      </header>

      {/* 필터 구현 필요 */}
      <div className='flex gap-3'>
        <button className='rounded-full border border-border bg-white px-4 py-2 text-sm font-medium hover:bg-gray-50'>
          난이도
        </button>

        <button className='rounded-full border border-border bg-white px-4 py-2 text-sm font-medium hover:bg-gray-50'>
          지역
        </button>
      </div>

      <div className='grid gap-5 md:grid-cols-2'>
        {parks.map((park) => (
          <ParkCard key={park.id} park={park} />
        ))}
      </div>

      <div ref={observerTarget} className='flex h-20 items-center justify-center'>
        {isFetchingNextPage && <p className='text-sm text-text-muted'>공원을 더 불러오는 중...</p>}

        {!hasNextPage && <p className='text-sm text-text-muted'>모든 공원을 불러왔습니다.</p>}
      </div>
    </section>
  );
};
