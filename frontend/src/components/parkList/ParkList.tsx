import { useEffect, useRef, useState } from 'react';
import { ParkCard } from './ParkCard';
import { useParks } from '../../hooks/useParks';
import { RequestStatus } from '../ui/RequestStatus';
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

  const { parks, total, fetchNextPage, hasNextPage, isFetching, isFetchingNextPage, isLoading, hasData, isFetchNextPageError, error, refetch } = useParks({
    pageSize: 20,
    keyword: debouncedKeyword,
    filters,
  });

  useEffect(() => {
    if (!observerTarget.current) return;
    if (!hasNextPage) return;
    if (error || isFetching) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
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
  }, [fetchNextPage, hasNextPage, isFetching, error]);

  const requestStatus = (
    <RequestStatus
      key={`${JSON.stringify([debouncedKeyword, filters])}:${isFetching}`}
      isFetching={isFetching}
      hasData={hasData}
      error={error}
      refetch={isFetchNextPageError ? fetchNextPage : refetch}
      loadingMessage={isFetchingNextPage ? '공원을 더 불러오는 중...' : undefined}
      className={!hasData && isLoading
        ? 'fixed bottom-24 left-1/2 z-10 w-[calc(100%-2rem)] max-w-sm -translate-x-1/2 rounded-card bg-white p-4 text-sm shadow-card'
        : 'my-4 rounded-card bg-white p-4 text-sm shadow-card'}
    />
  );

  return (
    <section className='px-page py-6 sm:py-8'>
      <header className='mb-5'>
        <h1 className='text-display font-semibold tracking-tight'>공원 목록</h1>
        <p className='mt-2 text-sm text-text-secondary'>{total != null ? `총 ${total}개의 공원` : '함께 산책할 공원을 찾아보세요'}</p>
      </header>
      <div className='my-4'>
        <SearchBar keyword={keyword} onKeywordChange={setKeyword} onFilterClick={() => setIsFilterOpen(true)} />
      </div>
      <div className='mb-6 empty:hidden'>
        <ActiveFilters filters={filters} onChange={setFilters} />
      </div>

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

      {!hasData ? (
        <>
          {isLoading && <ParkListSkeleton />}
          {requestStatus}
        </>
      ) : (
        <>


          <div className='grid gap-5 md:grid-cols-2'>
            {parks.map((park) => (
              <ParkCard key={park.id} park={park} />
            ))}
          </div>

          {requestStatus}
          <div ref={observerTarget} className='flex h-20 items-center justify-center'>
            {!hasNextPage && !error && <p className='text-sm text-text-muted'>모든 공원을 불러왔습니다.</p>}
          </div>
        </>
      )}
    </section>
  );
};
