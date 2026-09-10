import { useCallback, useEffect, useRef, useState } from 'react';
import { Map as MapLibreMap, Marker, NavigationControl, setWorkerUrl } from 'maplibre-gl';
import maplibreWorker from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { ParkMap } from '@/types/park';
import { runMapPerformanceTest, type PerformanceTestSummary } from './runMapPerformanceTest';

setWorkerUrl(maplibreWorker);

interface Props {
  mapContainer: React.RefObject<HTMLDivElement | null>;
  parks: ParkMap[];
}

export const useMarkerPerformanceTest = ({ mapContainer, parks }: Props) => {
  const mapRef = useRef<MapLibreMap | null>(null);
  const markersRef = useRef<Marker[]>([]);

  const [isReady, setIsReady] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentRun, setCurrentRun] = useState(0);
  const [result, setResult] = useState<PerformanceTestSummary | null>(null);

  /**
   * 지도 초기 생성
   */
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

    mapRef.current = map;

    map.addControl(
      new NavigationControl({
        showCompass: false,
      }),
      'top-right',
    );

    const handleLoad = () => {
      setIsReady(true);
    };

    map.on('load', handleLoad);

    return () => {
      map.off('load', handleLoad);

      markersRef.current.forEach((marker) => {
        marker.remove();
      });

      markersRef.current = [];

      map.remove();
      mapRef.current = null;

      setIsReady(false);
    };
  }, [mapContainer]);

  /**
   * Marker 업데이트
   *
   * parks가 API에서 로딩되거나
   * 132 / 500 / 1000 테스트 개수가 변경될 때 다시 생성
   */
  useEffect(() => {
    const map = mapRef.current;

    if (!map || !isReady) {
      return;
    }

    // 기존 Marker 제거
    markersRef.current.forEach((marker) => {
      marker.remove();
    });

    markersRef.current = [];

    // 새로운 Marker 생성
    const markers = parks.map((park) => {
      return new Marker().setLngLat([park.lon, park.lat]).addTo(map);
    });

    markersRef.current = markers;
  }, [parks, isReady]);

  /**
   * 성능 테스트 실행
   */
  const runPerformanceTest = useCallback(async () => {
    const map = mapRef.current;

    if (!map || !isReady || isTesting || parks.length === 0) {
      return;
    }

    setIsTesting(true);
    setProgress(0);
    setCurrentRun(0);
    setResult(null);

    try {
      const summary = await runMapPerformanceTest({
        map,
        mode: 'marker',
        pointCount: parks.length,

        onProgress: (current, total) => {
          setCurrentRun(current);
          setProgress((current / total) * 100);
        },
      });

      setResult(summary);
    } finally {
      setIsTesting(false);
    }
  }, [isReady, isTesting, parks.length]);

  return {
    isReady,
    isTesting,
    progress,
    currentRun,
    totalRuns: 10,
    result,
    runPerformanceTest,
  };
};
