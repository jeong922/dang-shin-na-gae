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
  hasSearchCondition: boolean;
}

interface Bounds {
  west: number;
  south: number;
  east: number;
  north: number;
}

export const MapView = ({ onSelectPark, searchResults, hasSearchCondition }: Props) => {
  const mapContainer = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const markersRef = useRef<Map<number, Marker>>(new Map());

  // 지도 이벤트 핸들러에서 최신 검색 상태를 참조하기 위한 Ref
  const hasSearchConditionRef = useRef(hasSearchCondition);

  useEffect(() => {
    hasSearchConditionRef.current = hasSearchCondition;
  }, [hasSearchCondition]);

  const [bounds, setBounds] = useState<Bounds | null>(null);

  const debouncedBounds = useDebounce(bounds, 500);

  const { parks, isLoading, isFetching, error, refetch } = useMapParks({
    ...(debouncedBounds ?? {}),
  });

  /**
   * 현재 지도에 표시할 공원
   *
   * 검색 조건이 있으면 검색 결과를 표시하고,
   * 검색 조건이 없으면 현재 지도 영역의 공원을 표시
   */
  const markerParks = useMemo(() => {
    if (hasSearchCondition) {
      return searchResults;
    }

    return parks;
  }, [hasSearchCondition, searchResults, parks]);

  /**
   * Marker 업데이트
   */
  const updateMarkers = useCallback(() => {
    if (!mapRef.current) return;

    const currentIds = new Set<number>();

    markerParks.forEach((park) => {
      currentIds.add(park.id);

      const existingMarker = markersRef.current.get(park.id);

      // 기존 Marker 재사용
      if (existingMarker) {
        existingMarker.getElement().onclick = () => {
          onSelectPark(park);
        };

        return;
      }

      // 새로운 Marker 생성
      const marker = new Marker().setLngLat([park.lon, park.lat]).addTo(mapRef.current!);

      const element = marker.getElement();

      element.style.cursor = 'pointer';

      element.onclick = () => {
        onSelectPark(park);
      };

      markersRef.current.set(park.id, marker);
    });

    // 더 이상 표시되지 않는 Marker 제거
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

    map.addControl(
      new NavigationControl({
        showCompass: false,
      }),
      'top-right',
    );

    map.on('load', updateBounds);

    map.on('moveend', () => {
      // 검색 조건이 있는 동안에는 지도 이동으로 /parks/map을 호출x
      if (hasSearchConditionRef.current) {
        return;
      }

      updateBounds();
    });

    mapRef.current = map;

    const currentMarkers = markersRef.current;

    return () => {
      currentMarkers.forEach((marker) => {
        marker.remove();
      });

      currentMarkers.clear();

      map.remove();
      mapRef.current = null;
    };
  }, [updateBounds]);

  /**
   * 검색 결과에 따른 지도 위치 이동
   */
  useEffect(() => {
    if (!mapRef.current) return;
    if (!hasSearchCondition) return;
    if (searchResults.length === 0) return;

    const map = mapRef.current;

    // 검색 결과가 하나인 경우
    if (searchResults.length === 1) {
      map.flyTo({
        center: [searchResults[0].lon, searchResults[0].lat],
        zoom: 15,
        duration: 700,
      });

      return;
    }

    // 검색 결과가 여러 개인 경우
    const searchBounds = new LngLatBounds();

    searchResults.forEach((park) => {
      searchBounds.extend([park.lon, park.lat]);
    });

    map.fitBounds(searchBounds, {
      padding: 80,
      maxZoom: 15,
      duration: 700,
    });
  }, [hasSearchCondition, searchResults]);

  /**
   * 검색 조건이 제거되면
   * 현재 지도 영역을 기준으로 공원 데이터를 다시 조회
   */
  useEffect(() => {
    if (!hasSearchCondition && mapRef.current) {
      updateBounds();
    }
  }, [hasSearchCondition, updateBounds]);

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
