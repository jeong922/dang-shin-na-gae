import 'maplibre-gl/dist/maplibre-gl.css';
import { useCallback, useRef, useState } from 'react';
import { LoaderCircle } from 'lucide-react';
import type { Bounds, ParkMap } from '../../types/park';
import { useMapParks } from '../../hooks/useMapParks';
import { useMapLibre } from '../../hooks/useMapLibre';
import { useDebounce } from '../../hooks/useDebounce';
import { LoadingOverlay } from '../ui/loading/LoadingOverlay';
import { Overlay } from '../ui/Overlay';
import { ErrorState } from '../ui/error/ErrorState';

interface Props {
  onSelectPark: (park: ParkMap) => void;
  searchResults: ParkMap[];
  hasSearchCondition: boolean;
}

export const MapView = ({ onSelectPark, searchResults, hasSearchCondition }: Props) => {
  const mapContainer = useRef<HTMLDivElement | null>(null);

  const [bounds, setBounds] = useState<Bounds | null>(null);

  const debouncedBounds = useDebounce(bounds, 500);

  const { parks, isLoading, isFetching, error, refetch } = useMapParks({
    ...(debouncedBounds ?? {}),
  });

  const handleBoundsChange = useCallback((nextBounds: Bounds) => {
    setBounds(nextBounds);
  }, []);

  useMapLibre({
    mapContainer,
    parks,
    searchResults,
    hasSearchCondition,
    onSelectPark,
    onBoundsChange: handleBoundsChange,
  });

  return (
    <div ref={mapContainer} className='relative h-[calc(100dvh-8rem)] rounded-2xl'>
      {isLoading && !bounds && <LoadingOverlay title='공원 정보를 불러오는 중' description='잠시만 기다려주세요.' />}

      {isFetching && (
        <div className='absolute bottom-6 left-1/2 flex -translate-x-1/2 items-center gap-2 rounded-full bg-white px-4 py-2 text-sm shadow-md z-10'>
          <LoaderCircle size={16} className='animate-spin' />
          공원 정보를 업데이트하는 중입니다.
        </div>
      )}

      {error && (
        <Overlay>
          <ErrorState
            title='공원 정보를 불러올 수 없습니다.'
            description={`서버와 연결할 수 없습니다.\n잠시 후 다시 시도해주세요.`}
            onRetry={refetch}
          />
        </Overlay>
      )}
    </div>
  );
};
