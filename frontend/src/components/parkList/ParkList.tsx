import { useEffect, useRef, useState } from 'react';
import { ParkCard } from './ParkCard';
import { useParks } from '../../hooks/useParks';
import { ErrorState } from '../common/error/ErrorState';
import { ParkListSkeleton } from './ParkListSkeleton';
import { SearchBar } from '../common/SearchBar';
import { useDebounce } from '../../hooks/useDebounce';
import type { ParkFilter as ParkFilterType } from '../../types/park';
import { BottomSheet } from '../common/BottomSheet';
import { ParkFilter } from '../common/ParkFilter';
import { ActiveFilters } from '../common/ActiveFilters';

export const ParkList = () => {
  const observerTarget = useRef<HTMLDivElement | null>(null);
  const [keyword, setKeyword] = useState<string>('');
  const debouncedKeyword = useDebounce(keyword, 300);
  const [filters, setFilters] = useState<ParkFilterType>({});
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  const { parks, total, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading, error, refetch } = useParks({
    pageSize: 20,
    keyword: debouncedKeyword,
    filters,
  });

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

  return (
    <section className='relative mx-auto my-6 max-w-5xl space-y-6 px-6'>
      <SearchBar keyword={keyword} onKeywordChange={setKeyword} onFilterClick={() => setIsFilterOpen(true)} />

      <ActiveFilters filters={filters} onChange={setFilters} />

      {isFilterOpen && (
        <BottomSheet open={isFilterOpen} onClose={() => setIsFilterOpen(false)} variant='filter'>
          <ParkFilter
            key={JSON.stringify(filters)}
            filters={filters}
            onChange={(nextFilters) => {
              setFilters(nextFilters);
              setIsFilterOpen(false);
            }}
          />
        </BottomSheet>
      )}

      {error ? (
        <ErrorState
          title='공원 목록을 불러올 수 없습니다.'
          description='잠시 후 다시 시도해주세요.'
          onRetry={refetch}
        />
      ) : isLoading && parks.length === 0 ? (
        <ParkListSkeleton />
      ) : (
        <>
          <header>
            <h1 className='text-3xl font-bold'>공원 목록</h1>

            <p className='mt-1 text-text-muted'>
              총 <span className='font-semibold text-brand'>{total}</span>
              개의 공원
            </p>
          </header>

          <div className='grid gap-5 md:grid-cols-2'>
            {parks.map((park) => (
              <ParkCard key={park.id} park={park} />
            ))}
          </div>

          <div ref={observerTarget} className='flex h-20 items-center justify-center'>
            {isFetchingNextPage && <p className='text-sm text-text-muted'>공원을 더 불러오는 중...</p>}

            {!hasNextPage && <p className='text-sm text-text-muted'>모든 공원을 불러왔습니다.</p>}
          </div>
        </>
      )}
    </section>
  );
};
