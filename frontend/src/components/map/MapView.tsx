import 'maplibre-gl/dist/maplibre-gl.css';
import { useCallback, useRef, useState } from 'react';
import type { Bounds, ParkMap } from '../../types/park';
import { useMapParks } from '../../hooks/useMapParks';
import { useMapLibre } from '../../hooks/useMapLibre';
import { useDebounce } from '../../hooks/useDebounce';
import { RequestStatus, type RequestState } from '../ui/RequestStatus';

interface Props {
  onSelectPark: (park: ParkMap) => void;
  searchResults: ParkMap[];
  selectedParkId: number | null;
  hasSearchCondition: boolean;
  searchStatus: RequestState;
  searchRequestKey: string;
}

export const MapView = ({
  onSelectPark,
  searchResults,
  hasSearchCondition,
  selectedParkId,
  searchStatus,
  searchRequestKey,
}: Props) => {
  const mapContainer = useRef<HTMLDivElement | null>(null);

  const [bounds, setBounds] = useState<Bounds | null>(null);

  const debouncedBounds = useDebounce(bounds, 500);

  const mapQuery = useMapParks({
    ...(debouncedBounds ?? {}),
  });

  const handleBoundsChange = useCallback((nextBounds: Bounds) => {
    setBounds(nextBounds);
  }, []);

  useMapLibre({
    mapContainer,
    parks: mapQuery.parks,
    searchResults,
    hasSearchCondition,
    onSelectPark,
    selectedParkId,
    onBoundsChange: handleBoundsChange,
  });

  const activeStatus = hasSearchCondition ? searchStatus : mapQuery;
  const activeRequestKey = hasSearchCondition
    ? `search:${searchRequestKey}`
    : `map:${JSON.stringify(debouncedBounds)}`;

  return (
    <div
      ref={mapContainer}
      className='relative h-[calc(100dvh-8rem)] rounded-2xl'
    >
      <RequestStatus
        key={`${activeRequestKey}:${activeStatus.isFetching}`}
        {...activeStatus}
        className='absolute bottom-6 left-1/2 z-10 w-[calc(100%-2rem)] max-w-sm -translate-x-1/2 rounded-2xl bg-white p-4 text-sm shadow-md'
      />
    </div>
  );
};
