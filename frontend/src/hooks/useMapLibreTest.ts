// import { LngLatBounds, Map as MapLibreMap, Marker, NavigationControl, setWorkerUrl } from 'maplibre-gl';

// import maplibreWorker from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';

// import { useCallback, useEffect, useMemo, useRef } from 'react';

// import type { Bounds, ParkMap } from '../types/park';

// import { runMapPerformanceTest } from '../../tests/performance/runMapPerformanceTest';

// setWorkerUrl(maplibreWorker);

// interface Props {
//   mapContainer: React.RefObject<HTMLDivElement | null>;

//   parks: ParkMap[];

//   searchResults: ParkMap[];

//   hasSearchCondition: boolean;

//   selectedParkId: number | null;

//   onSelectPark: (park: ParkMap) => void;

//   onBoundsChange: (bounds: Bounds) => void;
// }

// // ============================================================
// // 성능 테스트용
// // ============================================================

// const TEST_MARKER_COUNT = 500;

// export const useMapLibre = ({
//   mapContainer,
//   parks,
//   searchResults,
//   hasSearchCondition,
//   onSelectPark,
//   onBoundsChange,
// }: Props) => {
//   const mapRef = useRef<MapLibreMap | null>(null);

//   const markersRef = useRef<Map<number, Marker>>(new Map());

//   // 최신 검색 상태
//   const hasSearchConditionRef = useRef(hasSearchCondition);

//   // ------------------------------------------------------------
//   // 최신 검색 상태 저장
//   // ------------------------------------------------------------

//   useEffect(() => {
//     hasSearchConditionRef.current = hasSearchCondition;
//   }, [hasSearchCondition]);

//   // ------------------------------------------------------------
//   // 현재 지도에 표시할 공원
//   // ------------------------------------------------------------

//   const markerParks = useMemo(() => {
//     const targetParks = hasSearchCondition ? searchResults : parks;

//     // 성능 테스트용
//     return targetParks.slice(0, TEST_MARKER_COUNT);
//   }, [hasSearchCondition, searchResults, parks]);

//   // ------------------------------------------------------------
//   // 현재 지도 영역 전달
//   // ------------------------------------------------------------

//   const updateBounds = useCallback(() => {
//     if (!mapRef.current) return;

//     const mapBounds = mapRef.current.getBounds();

//     onBoundsChange({
//       west: Number(mapBounds.getWest().toFixed(3)),

//       south: Number(mapBounds.getSouth().toFixed(3)),

//       east: Number(mapBounds.getEast().toFixed(3)),

//       north: Number(mapBounds.getNorth().toFixed(3)),
//     });
//   }, [onBoundsChange]);

//   // ------------------------------------------------------------
//   // Marker 업데이트
//   // ------------------------------------------------------------

//   const updateMarkers = useCallback(() => {
//     if (!mapRef.current) return;

//     const currentIds = new Set<number>();

//     // ----------------------------------------------------------
//     // Marker 생성 / 재사용
//     // ----------------------------------------------------------

//     markerParks.forEach((park) => {
//       currentIds.add(park.id);

//       const existingMarker = markersRef.current.get(park.id);

//       // 기존 Marker 재사용
//       if (existingMarker) {
//         existingMarker.getElement().onclick = () => {
//           onSelectPark(park);
//         };

//         return;
//       }

//       // 새로운 Marker 생성
//       const marker = new Marker().setLngLat([park.lon, park.lat]).addTo(mapRef.current!);

//       const element = marker.getElement();

//       element.style.cursor = 'pointer';

//       element.onclick = () => {
//         onSelectPark(park);
//       };

//       markersRef.current.set(park.id, marker);
//     });

//     // ----------------------------------------------------------
//     // 더 이상 필요 없는 Marker 제거
//     // ----------------------------------------------------------

//     markersRef.current.forEach((marker, id) => {
//       if (!currentIds.has(id)) {
//         marker.remove();

//         markersRef.current.delete(id);
//       }
//     });
//   }, [markerParks, onSelectPark]);

//   // ------------------------------------------------------------
//   // 지도 초기 생성
//   // ------------------------------------------------------------

//   useEffect(() => {
//     if (!mapContainer.current || mapRef.current) {
//       return;
//     }

//     const map = new MapLibreMap({
//       container: mapContainer.current,

//       style: 'https://tiles.openfreemap.org/styles/bright',

//       center: [126.978, 37.5665],

//       zoom: 13,

//       minZoom: 10,

//       maxZoom: 18,

//       maxBounds: [
//         [126.6, 37.3],
//         [127.3, 37.8],
//       ],
//     });

//     map.addControl(
//       new NavigationControl({
//         showCompass: false,
//       }),
//       'top-right',
//     );

//     // ----------------------------------------------------------
//     // 지도 로드
//     // ----------------------------------------------------------

//     map.on('load', updateBounds);

//     // ----------------------------------------------------------
//     // 지도 이동
//     // ----------------------------------------------------------

//     map.on('moveend', () => {
//       if (hasSearchConditionRef.current) {
//         return;
//       }

//       updateBounds();
//     });

//     mapRef.current = map;

//     const currentMarkers = markersRef.current;

//     // ----------------------------------------------------------
//     // Cleanup
//     // ----------------------------------------------------------

//     return () => {
//       currentMarkers.forEach((marker) => {
//         marker.remove();
//       });

//       currentMarkers.clear();

//       map.remove();

//       mapRef.current = null;
//     };
//   }, [mapContainer, updateBounds]);

//   // ------------------------------------------------------------
//   // Marker 업데이트
//   // ------------------------------------------------------------

//   useEffect(() => {
//     updateMarkers();
//   }, [updateMarkers]);

//   // ------------------------------------------------------------
//   // 검색 결과 지도 이동
//   // ------------------------------------------------------------

//   useEffect(() => {
//     if (!mapRef.current) return;

//     if (!hasSearchCondition) return;

//     if (searchResults.length === 0) {
//       return;
//     }

//     const map = mapRef.current;

//     // 검색 결과가 하나
//     if (searchResults.length === 1) {
//       map.flyTo({
//         center: [searchResults[0].lon, searchResults[0].lat],

//         zoom: 15,

//         duration: 700,
//       });

//       return;
//     }

//     // 검색 결과가 여러 개
//     const searchBounds = new LngLatBounds();

//     searchResults.forEach((park) => {
//       searchBounds.extend([park.lon, park.lat]);
//     });

//     map.fitBounds(searchBounds, {
//       padding: 80,

//       maxZoom: 15,

//       duration: 700,
//     });
//   }, [hasSearchCondition, searchResults]);

//   // ------------------------------------------------------------
//   // 검색 조건 제거
//   // ------------------------------------------------------------

//   useEffect(() => {
//     if (!hasSearchCondition) {
//       updateBounds();
//     }
//   }, [hasSearchCondition, updateBounds]);

//   // ------------------------------------------------------------
//   // 성능 테스트
//   // ------------------------------------------------------------

//   const runPerformanceTest = useCallback(() => {
//     if (!mapRef.current) {
//       console.warn('Map이 아직 준비되지 않았습니다.');

//       return;
//     }

//     return runMapPerformanceTest(mapRef.current);
//   }, []);

//   return {
//     runPerformanceTest,
//   };
// };

import { GeoJSONSource, LngLatBounds, Map as MapLibreMap, NavigationControl, setWorkerUrl } from 'maplibre-gl';

import maplibreWorker from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';

import { useCallback, useEffect, useMemo, useRef } from 'react';

import type { Bounds, ParkMap } from '../types/park';

import { runMapPerformanceTest } from '../../tests/performance/runMapPerformanceTest';

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

  // 지도 이벤트에서 최신 검색 상태
  const hasSearchConditionRef = useRef(hasSearchCondition);

  // 최신 공원 목록
  const markerParksRef = useRef<ParkMap[]>([]);

  // 현재 선택된 공원
  const selectedParkIdRef = useRef<number | null>(null);

  // 현재 hover 중인 공원
  const hoveredParkIdRef = useRef<number | null>(null);

  // ------------------------------------------------------------
  // 최신 검색 상태 저장
  // ------------------------------------------------------------

  useEffect(() => {
    hasSearchConditionRef.current = hasSearchCondition;
  }, [hasSearchCondition]);

  // ------------------------------------------------------------
  // 현재 지도에 표시할 공원
  // ------------------------------------------------------------

  const markerParks = useMemo(() => {
    return hasSearchCondition ? searchResults : parks;
  }, [hasSearchCondition, searchResults, parks]);

  // ------------------------------------------------------------
  // 최신 공원 목록 저장
  // ------------------------------------------------------------

  useEffect(() => {
    markerParksRef.current = markerParks;
  }, [markerParks]);

  // ------------------------------------------------------------
  // 현재 지도 영역 전달
  // ------------------------------------------------------------

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

  // ------------------------------------------------------------
  // GeoJSON 생성
  // ------------------------------------------------------------

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

  // ------------------------------------------------------------
  // GeoJSON Source 업데이트
  // ------------------------------------------------------------

  const updateParkSource = useCallback(() => {
    const map = mapRef.current;

    if (!map) return;

    const source = map.getSource('parks-source') as GeoJSONSource | undefined;

    if (!source) return;

    source.setData(createParkGeoJSON(markerParks));
  }, [markerParks]);

  // ------------------------------------------------------------
  // 지도 초기 생성
  // ------------------------------------------------------------

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) {
      return;
    }

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

    // ----------------------------------------------------------
    // 지도 로드
    // ----------------------------------------------------------

    map.on('load', () => {
      map.addSource('parks-source', {
        type: 'geojson',

        data: {
          type: 'FeatureCollection',

          features: [],
        },
      });

      // --------------------------------------------------------
      // Glow Layer
      // --------------------------------------------------------

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

      // --------------------------------------------------------
      // Main Layer
      // --------------------------------------------------------

      map.addLayer({
        id: 'parks-layer',

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

      // --------------------------------------------------------
      // Selected Ring
      // --------------------------------------------------------

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

    // ----------------------------------------------------------
    // Click
    // ----------------------------------------------------------

    map.on('click', 'parks-layer', (event) => {
      const feature = event.features?.[0];

      if (!feature) return;

      const parkId = Number(feature.id);

      if (!Number.isFinite(parkId)) {
        return;
      }

      const park = markerParksRef.current.find((park) => park.id === parkId);

      if (park) {
        onSelectPark(park);
      }
    });

    // ----------------------------------------------------------
    // Hover 시작
    // ----------------------------------------------------------

    map.on('mouseenter', 'parks-layer', (event) => {
      map.getCanvas().style.cursor = 'pointer';

      const feature = event.features?.[0];

      if (!feature) return;

      const parkId = Number(feature.id);

      if (!Number.isFinite(parkId)) {
        return;
      }

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

    // ----------------------------------------------------------
    // Hover 종료
    // ----------------------------------------------------------

    map.on('mouseleave', 'parks-layer', () => {
      map.getCanvas().style.cursor = '';

      if (hoveredParkIdRef.current === null) {
        return;
      }

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

    // ----------------------------------------------------------
    // 지도 이동
    // ----------------------------------------------------------

    map.on('moveend', () => {
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

  // ------------------------------------------------------------
  // 선택 상태
  // ------------------------------------------------------------

  useEffect(() => {
    const map = mapRef.current;

    if (!map) return;

    if (!map.getSource('parks-source')) {
      return;
    }

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

    selectedParkIdRef.current = selectedParkId;
  }, [selectedParkId]);

  // ------------------------------------------------------------
  // GeoJSON 데이터 변경
  // ------------------------------------------------------------

  useEffect(() => {
    updateParkSource();
  }, [updateParkSource]);

  // ------------------------------------------------------------
  // 검색 결과 지도 이동
  // ------------------------------------------------------------

  useEffect(() => {
    if (!mapRef.current) return;

    if (!hasSearchCondition) return;

    if (searchResults.length === 0) {
      return;
    }

    const map = mapRef.current;

    if (searchResults.length === 1) {
      map.flyTo({
        center: [searchResults[0].lon, searchResults[0].lat],

        zoom: 15,

        duration: 700,
      });

      return;
    }

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

  // ------------------------------------------------------------
  // 검색 조건 제거
  // ------------------------------------------------------------

  useEffect(() => {
    if (!hasSearchCondition) {
      updateBounds();
    }
  }, [hasSearchCondition, updateBounds]);

  // ------------------------------------------------------------
  // 성능 테스트
  // ------------------------------------------------------------

  const runPerformanceTest = useCallback(() => {
    if (!mapRef.current) {
      console.warn('Map이 아직 준비되지 않았습니다.');

      return;
    }

    return runMapPerformanceTest(mapRef.current);
  }, []);

  return {
    runPerformanceTest,
  };
};
