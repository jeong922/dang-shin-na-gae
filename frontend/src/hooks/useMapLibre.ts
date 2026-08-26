import { GeoJSONSource, LngLatBounds, Map as MapLibreMap, NavigationControl, setWorkerUrl } from 'maplibre-gl';
import type { FilterSpecification } from 'maplibre-gl';
import maplibreWorker from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import { useCallback, useEffect, useMemo, useRef } from 'react';
import type { Bounds, ParkMap } from '../types/park';

setWorkerUrl(maplibreWorker);

interface Props {
  mapContainer: React.RefObject<HTMLDivElement | null>;
  parks: ParkMap[];
  searchResults: ParkMap[];
  hasSearchCondition: boolean;
  selectedParkId: number | null;
  onSelectPark: (park: ParkMap) => void;
  onBoundsChange: (bounds: Bounds) => void;
}

export const useMapLibre = ({
  mapContainer,
  parks,
  searchResults,
  hasSearchCondition,
  selectedParkId,
  onSelectPark,
  onBoundsChange,
}: Props) => {
  const mapRef = useRef<MapLibreMap | null>(null);

  // 지도 이벤트에서 최신 검색 상태를 참조하기 위한 Ref
  const hasSearchConditionRef = useRef(hasSearchCondition);

  // 지도 클릭 이벤트에서 최신 공원 목록을 참조하기 위한 Ref
  const markerParksRef = useRef<ParkMap[]>([]);

  /**
   * MapLibre에서 현재 선택된 공원 ID
   *
   * React의 selectedParkId와 동기화하기 위해 사용
   */
  const selectedParkIdRef = useRef<number | null>(null);

  /**
   * 현재 hover 중인 공원 ID
   */
  const hoveredParkIdRef = useRef<number | null>(null);

  /**
   * 최신 검색 상태 저장
   */
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
   * 지도 클릭 이벤트에서 사용할
   * 최신 공원 목록 저장
   */
  useEffect(() => {
    markerParksRef.current = markerParks;
  }, [markerParks]);

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
   * 공원 목록을 MapLibre에서 사용할 GeoJSON으로 변환
   *
   * Feature의 id는 feature-state를 통한
   * 선택/hover 상태 관리에 사용
   */
  const createParkGeoJSON = (parks: ParkMap[]) => ({
    type: 'FeatureCollection' as const,
    features: parks.map((park) => ({
      id: park.id,
      type: 'Feature' as const,
      geometry: {
        type: 'Point' as const,
        coordinates: [park.lon, park.lat] as [number, number],
      },
      properties: {
        difficulty: park.difficulty,
      },
    })),
  });

  /**
   * 현재 공원 데이터를 GeoJSON Source에 반영
   *
   * 공원 데이터가 변경될 때 Source의 데이터를 갱신
   * 선택/hover 상태는 별도의 feature-state로 관리
   */
  const updateParkSource = useCallback(() => {
    const map = mapRef.current;

    if (!map) return;

    const source = map.getSource('parks-source') as GeoJSONSource | undefined;

    if (!source) return;

    source.setData(createParkGeoJSON(markerParks));
  }, [markerParks]);

  // 지도 초기 생성
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

    // 지도 로드 완료
    map.on('load', () => {
      // 공원 Polygon Source
      map.addSource('park-polygons-source', {
        type: 'geojson',
        data: '/data/final_park_polygons.geojson',
      });

      map.addLayer({
        id: 'park-polygons-fill',
        type: 'fill',
        source: 'park-polygons-source',

        filter: ['==', ['get', 'park_id'], -1],

        paint: {
          'fill-color': '#22C55E',
          'fill-opacity': 0.18,
        },
      });

      map.addLayer({
        id: 'park-polygons-outline',
        type: 'line',
        source: 'park-polygons-source',

        filter: ['==', ['get', 'park_id'], -1],

        paint: {
          'line-color': '#16A34A',
          'line-width': 3,
          'line-opacity': 0.9,
        },
      });

      //GeoJSON Source
      map.addSource('parks-source', {
        type: 'geojson',

        data: {
          type: 'FeatureCollection',
          features: [],
        },
      });

      //  1. 선택 / hover Glow Layer
      map.addLayer({
        id: 'parks-glow-layer',

        type: 'circle',

        source: 'parks-source',

        paint: {
          'circle-color': [
            'match',
            ['get', 'difficulty'],

            'easy',
            '#22C55E',

            'medium',
            '#F59E0B',

            'hard',
            '#EF4444',

            'expert',
            '#7C3AED',

            '#64748B',
          ],

          'circle-radius': [
            'case',

            ['boolean', ['feature-state', 'selected'], false],
            22,

            ['boolean', ['feature-state', 'hover'], false],
            18,

            8,
          ],

          'circle-opacity': [
            'case',

            ['boolean', ['feature-state', 'selected'], false],
            0.22,

            ['boolean', ['feature-state', 'hover'], false],
            0.18,

            0,
          ],

          'circle-blur': 0.8,
        },
      });

      // 2. 메인 공원 마커
      map.addLayer({
        id: 'parks-layer',

        type: 'circle',

        source: 'parks-source',

        paint: {
          // 난이도별 색상
          'circle-color': [
            'match',
            ['get', 'difficulty'],

            'easy',
            '#22C55E',

            'medium',
            '#F59E0B',

            'hard',
            '#EF4444',

            'expert',
            '#7C3AED',

            '#64748B',
          ],

          'circle-radius': [
            'case',

            ['boolean', ['feature-state', 'selected'], false],
            10,

            ['boolean', ['feature-state', 'hover'], false],
            9,

            7,
          ],

          'circle-stroke-width': [
            'case',

            ['boolean', ['feature-state', 'selected'], false],
            3,

            ['boolean', ['feature-state', 'hover'], false],
            2.5,

            2,
          ],

          'circle-stroke-color': '#FFFFFF',

          'circle-opacity': [
            'case',

            ['boolean', ['feature-state', 'selected'], false],
            1,

            ['boolean', ['feature-state', 'hover'], false],
            1,

            0.92,
          ],
        },
      });

      // 3. 선택 상태 외곽 Ring
      map.addLayer({
        id: 'parks-selected-ring',

        type: 'circle',

        source: 'parks-source',

        paint: {
          'circle-color': 'rgba(255, 255, 255, 0)',
          'circle-radius': 14,
          'circle-stroke-width': ['case', ['boolean', ['feature-state', 'selected'], false], 2, 0],
          'circle-stroke-color': '#FFFFFF',
          'circle-opacity': 1,
        },
      });

      updateBounds();
    });

    /**
     * 공원 클릭
     *
     * 클릭 시에는 React 상태만 변경
     *
     * 실제 MapLibre selected 상태는
     * selectedParkId 변경을 감지하는 useEffect에서 처리
     */
    map.on('click', 'parks-layer', (event) => {
      const feature = event.features?.[0];

      if (!feature) return;

      const parkId = Number(feature.id);

      if (!Number.isFinite(parkId)) return;

      /**
       * 최신 공원 데이터에서 실제 공원 찾기
       */
      const park = markerParksRef.current.find((park) => park.id === parkId);

      if (park) {
        onSelectPark(park);
      }
    });

    // Hover 시작
    map.on('mouseenter', 'parks-layer', (event) => {
      map.getCanvas().style.cursor = 'pointer';

      const feature = event.features?.[0];

      if (!feature) return;

      const parkId = Number(feature.id);

      if (!Number.isFinite(parkId)) return;

      // 이전 hover 상태 제거
      if (hoveredParkIdRef.current !== null) {
        map.setFeatureState(
          {
            source: 'parks-source',
            id: hoveredParkIdRef.current,
          },
          {
            hover: false,
          },
        );
      }

      // 현재 hover 상태 설정
      map.setFeatureState(
        {
          source: 'parks-source',
          id: parkId,
        },
        {
          hover: true,
        },
      );

      hoveredParkIdRef.current = parkId;
    });

    // Hover 종료
    map.on('mouseleave', 'parks-layer', () => {
      map.getCanvas().style.cursor = '';

      if (hoveredParkIdRef.current === null) return;

      map.setFeatureState(
        {
          source: 'parks-source',
          id: hoveredParkIdRef.current,
        },
        {
          hover: false,
        },
      );

      hoveredParkIdRef.current = null;
    });

    // 지도 이동 완료
    map.on('moveend', () => {
      /**
       * 검색 조건이 있는 동안에는
       * 지도 이동으로 /parks/map을 호출하지 않음
       */
      if (hasSearchConditionRef.current) {
        return;
      }

      updateBounds();
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [mapContainer, onSelectPark, updateBounds]);

  useEffect(() => {
    const map = mapRef.current;

    if (!map) return;

    // Source가 아직 생성되지 않은 경우
    if (!map.getSource('parks-source')) return;

    // 이전에 선택되어 있던 공원 해제
    const previousSelectedId = selectedParkIdRef.current;

    if (previousSelectedId !== null && previousSelectedId !== selectedParkId) {
      map.setFeatureState(
        {
          source: 'parks-source',
          id: previousSelectedId,
        },
        {
          selected: false,
        },
      );
    }

    // 선택된 공원의 Polygon만 표시
    const polygonFilter: FilterSpecification =
      selectedParkId !== null ? ['==', ['get', 'park_id'], selectedParkId] : ['==', ['get', 'park_id'], -1];

    if (map.getLayer('park-polygons-fill')) {
      map.setFilter('park-polygons-fill', polygonFilter);
    }

    if (map.getLayer('park-polygons-outline')) {
      map.setFilter('park-polygons-outline', polygonFilter);
    }

    // 새로운 공원 선택
    if (selectedParkId !== null) {
      map.setFeatureState(
        {
          source: 'parks-source',
          id: selectedParkId,
        },
        {
          selected: true,
        },
      );
    }

    // 현재 선택 상태 저장
    selectedParkIdRef.current = selectedParkId;
  }, [selectedParkId]);

  // 공원 데이터 변경
  useEffect(() => {
    updateParkSource();
  }, [updateParkSource]);

  // 검색 결과에 따른 지도 이동
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

  //  검색 조건 제거
  useEffect(() => {
    if (!hasSearchCondition) {
      updateBounds();
    }
  }, [hasSearchCondition, updateBounds]);
};
