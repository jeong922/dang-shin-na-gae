import 'maplibre-gl/dist/maplibre-gl.css';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Map as MapLibreMap, NavigationControl, Marker, LngLatBounds } from 'maplibre-gl';
import { LoaderCircle } from 'lucide-react';
import type { ParkMap } from '../../types/park';
import { useMapParks } from '../../hooks/useMapParks';
import { useDebounce } from '../../hooks/useDebounce';
import { LoadingOverlay } from '../ui/loading/LoadingOverlay';
import { Overlay } from '../ui/Overlay';
import { ErrorState } from '../ui/error/ErrorState';

interface Props {
  onSelectPark: (park: ParkMap) => void;
  searchResults: ParkMap[];
  hasSearchKeyword: boolean;
}

interface Bounds {
  west: number;
  south: number;
  east: number;
  north: number;
}

export const MapView = ({ onSelectPark, searchResults, hasSearchKeyword }: Props) => {
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const markersRef = useRef<Map<number, Marker>>(new Map());
  const isSearchMoveRef = useRef(false);
  const hasSearchKeywordRef = useRef(hasSearchKeyword);

  useEffect(() => {
    hasSearchKeywordRef.current = hasSearchKeyword;
  }, [hasSearchKeyword]);

  const [bounds, setBounds] = useState<Bounds | null>(null);
  const debouncedBounds = useDebounce(bounds, 500);

  const { parks, isLoading, isFetching, error, refetch } = useMapParks({
    ...(debouncedBounds ?? {}),
  });

  const markerParks = useMemo(() => {
    if (hasSearchKeyword) {
      return searchResults;
    }
    return parks;
  }, [hasSearchKeyword, searchResults, parks]);

  /**
   * Marker 업데이트
   */
  const updateMarkers = useCallback(() => {
    if (!mapRef.current) return;

    const currentIds = new Set<number>();

    markerParks.forEach((park) => {
      currentIds.add(park.id);
      const existingMarker = markersRef.current.get(park.id);

      if (existingMarker) {
        existingMarker.getElement().onclick = () => onSelectPark(park);
        return;
      }

      const marker = new Marker().setLngLat([park.lon, park.lat]).addTo(mapRef.current!);
      const element = marker.getElement();
      element.style.cursor = 'pointer';
      element.onclick = () => onSelectPark(park);

      markersRef.current.set(park.id, marker);
    });

    markersRef.current.forEach((marker, id) => {
      if (!currentIds.has(id)) {
        marker.remove();
        markersRef.current.delete(id);
      }
    });
  }, [markerParks, onSelectPark]);

  useEffect(() => {
    updateMarkers();
  }, [updateMarkers]);

  /**
   * 현재 지도 영역 저장
   */
  const updateBounds = useCallback(() => {
    if (!mapRef.current) return;

    const mapBounds = mapRef.current.getBounds();
    setBounds({
      west: Number(mapBounds.getWest().toFixed(3)),
      south: Number(mapBounds.getSouth().toFixed(3)),
      east: Number(mapBounds.getEast().toFixed(3)),
      north: Number(mapBounds.getNorth().toFixed(3)),
    });
  }, []);

  /**
   * 지도 초기 생성
   */
  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    const map = new MapLibreMap({
      container: mapContainer.current,
      style: 'https://tiles.openfreemap.org/styles/bright',
      center: [126.978, 37.5665],
      zoom: 13,
      minZoom: 10,
      maxZoom: 18,
      maxBounds: [
        [126.6, 37.3],
        [127.3, 37.8],
      ],
    });

    map.addControl(new NavigationControl({ showCompass: false }), 'top-right');

    map.on('load', updateBounds);

    map.on('moveend', () => {
      if (hasSearchKeywordRef.current) return;

      if (isSearchMoveRef.current) {
        isSearchMoveRef.current = false;
        return;
      }
      updateBounds();
    });

    mapRef.current = map;

    const currentMarkers = markersRef.current;

    return () => {
      currentMarkers.forEach((marker) => marker.remove());
      currentMarkers.clear();
      map.remove();
      mapRef.current = null;
    };
  }, [updateBounds]);

  /**
   * 검색 결과에 따른 지도 위치 이동
   */
  useEffect(() => {
    if (!mapRef.current || !hasSearchKeyword || searchResults.length === 0) return;

    const map = mapRef.current;
    isSearchMoveRef.current = true;

    if (searchResults.length === 1) {
      map.flyTo({
        center: [searchResults[0].lon, searchResults[0].lat],
        zoom: 15,
        duration: 700,
      });
      return;
    }

    const bounds = new LngLatBounds();
    searchResults.forEach((park) => {
      bounds.extend([park.lon, park.lat]);
    });

    map.fitBounds(bounds, {
      padding: 80,
      maxZoom: 15,
      duration: 700,
    });
  }, [hasSearchKeyword, searchResults]);

  useEffect(() => {
    if (!hasSearchKeyword && mapRef.current) {
      updateBounds();
    }
  }, [hasSearchKeyword, updateBounds]);

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
