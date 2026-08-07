import { lazy, Suspense, useCallback, useState } from 'react';
import type { ParkMap } from '../../types/park';
import { BottomSheet } from '../ui/BottomSheet';
import { ParkDetailContent } from './ParkDetailContent';
import { SearchBar } from '../ui/SearchBar';
import { useSearchParks } from '../../hooks/useSearchParks';
import { useDebounce } from '../../hooks/useDebounce';

const MapView = lazy(() =>
  import('./MapView').then(({ MapView }) => ({
    default: MapView,
  })),
);

export const ParkMapContainer = () => {
  const [selectedPark, setSelectedPark] = useState<ParkMap | null>(null);
  const [keyword, setKeyword] = useState('');

  const debouncedKeyword = useDebounce(keyword, 300);

  const { parks: searchResults } = useSearchParks({
    keyword: debouncedKeyword,
  });

  const hasSearchKeyword = debouncedKeyword.trim().length > 0;

  const handleSelectPark = useCallback((park: ParkMap) => {
    setSelectedPark(park);
  }, []);

  const handleClose = useCallback(() => {
    setSelectedPark(null);
  }, []);

  return (
    <section className='relative h-[calc(100dvh-8rem)]'>
      <div className='absolute top-4 left-4 right-16 z-10 pointer-events-auto'>
        <SearchBar keyword={keyword} onKeywordChange={setKeyword} onFilterClick={() => true} />
      </div>

      <Suspense fallback={<div className='h-[calc(100dvh-8rem)] animate-pulse rounded-2xl bg-slate-100' />}>
        <MapView onSelectPark={handleSelectPark} searchResults={searchResults} hasSearchKeyword={hasSearchKeyword} />
      </Suspense>

      <BottomSheet open={!!selectedPark} onClose={handleClose}>
        {selectedPark && <ParkDetailContent park={selectedPark} />}
      </BottomSheet>
    </section>
  );
};
