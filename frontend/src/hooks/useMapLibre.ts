import { Map as MapLibreMap, NavigationControl, Marker, LngLatBounds, setWorkerUrl } from 'maplibre-gl';
import maplibreWorker from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import { useCallback, useEffect, useMemo, useRef } from 'react';
import type { Bounds, ParkMap } from '../types/park';

setWorkerUrl(maplibreWorker);

interface Props {
  mapContainer: React.RefObject<HTMLDivElement | null>;
  parks: ParkMap[];
  searchResults: ParkMap[];
  hasSearchCondition: boolean;
  onSelectPark: (park: ParkMap) => void;
  onBoundsChange: (bounds: Bounds) => void;
}

export const useMapLibre = ({
  mapContainer,
  parks,
  searchResults,
  hasSearchCondition,
  onSelectPark,
  onBoundsChange,
}: Props) => {
  const mapRef = useRef<MapLibreMap | null>(null);
  const markersRef = useRef<Map<number, Marker>>(new Map());

  // 지도 이벤트에서 최신 검색 상태를 참조하기 위한 Ref
  const hasSearchConditionRef = useRef(hasSearchCondition);

  useEffect(() => {
    hasSearchConditionRef.current = hasSearchCondition;
  }, [hasSearchCondition]);

  /**
   * 현재 지도에 표시할 공원
   *
   * 검색 조건이 있으면 검색 결과를 표시하고,
   * 검색 조건이 없으면 현재 지도 영역의 공원을 표시
   */
  const markerParks = useMemo(() => {
    return hasSearchCondition ? searchResults : parks;
  }, [hasSearchCondition, searchResults, parks]);

  /**
   * 현재 지도 영역을 부모 컴포넌트로 전달
   */
  const updateBounds = useCallback(() => {
    if (!mapRef.current) return;

    const mapBounds = mapRef.current.getBounds();

    onBoundsChange({
      west: Number(mapBounds.getWest().toFixed(3)),
      south: Number(mapBounds.getSouth().toFixed(3)),
      east: Number(mapBounds.getEast().toFixed(3)),
      north: Number(mapBounds.getNorth().toFixed(3)),
    });
  }, [onBoundsChange]);

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
  }, [mapContainer, updateBounds]);

  /**
   * Marker 업데이트
   */
  useEffect(() => {
    updateMarkers();
  }, [updateMarkers]);

  /**
   * 검색 결과에 따른 지도 이동
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
   * 현재 지도 영역을 다시 조회
   */
  useEffect(() => {
    if (!hasSearchCondition) {
      updateBounds();
    }
  }, [hasSearchCondition, updateBounds]);
};
