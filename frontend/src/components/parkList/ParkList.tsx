import { useEffect, useRef, useState } from 'react';
import { ParkCard } from './ParkCard';
import { useParks } from '../../hooks/useParks';
import { ErrorState } from '../ui/error/ErrorState';
import { ParkListSkeleton } from './ParkListSkeleton';
import { SearchBar } from '../ui/SearchBar';
import { useDebounce } from '../../hooks/useDebounce';
import { BottomSheet } from '../ui/BottomSheet';
import { ParkFilter } from '../park/ParkFilter';
import { ActiveFilters } from '../park/ActiveFilters';

export const ParkList = () => {
  const observerTarget = useRef<HTMLDivElement | null>(null);

  const [keyword, setKeyword] = useState('');
  const [filters, setFilters] = useState({});
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  const debouncedKeyword = useDebounce(keyword, 300);

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
    <section>
      <SearchBar keyword={keyword} onKeywordChange={setKeyword} onFilterClick={() => setIsFilterOpen(true)} />

      <ActiveFilters filters={filters} onChange={setFilters} />

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

      {error ? (
        <ErrorState
          title='공원 목록을 불러올 수 없습니다.'
          description='공원 목록을 불러오는 중 문제가 발생했습니다.'
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
