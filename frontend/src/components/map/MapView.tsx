import 'maplibre-gl/dist/maplibre-gl.css';
import { useCallback, useRef, useState } from 'react';
import type { Bounds, ParkMap } from '../../types/park';
import { useMapParks } from '../../hooks/useMapParks';
import { useMapLibre } from '../../hooks/useMapLibre';
import { useDebounce } from '../../hooks/useDebounce';
import { MapRequestStatus, type MapRequestState } from './MapRequestStatus';

interface Props {
  onSelectPark: (park: ParkMap) => void;
  searchResults: ParkMap[];
  selectedParkId: number | null;
  hasSearchCondition: boolean;
  searchStatus: MapRequestState;
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
  const activeRequestKey = hasSearchCondition ? `search:${searchRequestKey}` : `map:${JSON.stringify(debouncedBounds)}`;

  return (
    <div ref={mapContainer} className='relative h-[calc(100dvh-8rem)] rounded-2xl'>
      <MapRequestStatus
        // 조건 변경 및 재시도마다 지연 안내 타이머를 새로 시작합니다.
        key={`${activeRequestKey}:${activeStatus.isFetching}`}
        {...activeStatus}
      />
    </div>
  );
};
