import { useCallback, useEffect, useRef, useState } from 'react';
import { Map as MapLibreMap, NavigationControl, setWorkerUrl } from 'maplibre-gl';
import maplibreWorker from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import type { FeatureCollection, Point } from 'geojson';

import type { ParkMap } from '@/types/park';
import { runMapPerformanceTest, type PerformanceTestSummary } from './runMapPerformanceTest';

setWorkerUrl(maplibreWorker);

interface Props {
  mapContainer: React.RefObject<HTMLDivElement | null>;
  parks: ParkMap[];
}

interface ParkProperties {
  id: number;
  name: string;
  difficulty: ParkMap['difficulty'];
}

export const useGeoJSONPerformanceTest = ({ mapContainer, parks }: Props) => {
  const mapRef = useRef<MapLibreMap | null>(null);

  const [isReady, setIsReady] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentRun, setCurrentRun] = useState(0);
  const [result, setResult] = useState<PerformanceTestSummary | null>(null);

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) {
      return;
    }

    const map = new MapLibreMap({
      container: mapContainer.current,
      style: 'https://tiles.openfreemap.org/styles/bright',
      center: [126.978, 37.5665],
      zoom: 12,
      minZoom: 10,
      maxZoom: 18,
      maxBounds: [
        [126.6, 37.3],
        [127.3, 37.8],
      ],
    });

    mapRef.current = map;

    map.addControl(new NavigationControl(), 'top-right');

    map.on('load', () => {
      const geoJSON: FeatureCollection<Point, ParkProperties> = {
        type: 'FeatureCollection',
        features: parks.map((park) => ({
          type: 'Feature',
          id: park.id,
          geometry: {
            type: 'Point',
            coordinates: [park.lon, park.lat],
          },
          properties: {
            id: park.id,
            name: park.name,
            difficulty: park.difficulty,
          },
        })),
      };

      map.addSource('performance-parks', {
        type: 'geojson',
        data: geoJSON,
        promoteId: 'id',
      });

      map.addLayer({
        id: 'performance-park-glow',
        type: 'circle',
        source: 'performance-parks',
        paint: {
          'circle-radius': 12,
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
            '#6B7280',
          ],
          'circle-opacity': 0.18,
          'circle-blur': 0.6,
        },
      });

      map.addLayer({
        id: 'performance-park-main',
        type: 'circle',
        source: 'performance-parks',
        paint: {
          'circle-radius': 7,
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
            '#6B7280',
          ],
          'circle-stroke-width': 2,
          'circle-stroke-color': '#FFFFFF',
        },
      });

      map.addLayer({
        id: 'performance-park-selected',
        type: 'circle',
        source: 'performance-parks',
        paint: {
          'circle-radius': 11,
          'circle-color': 'transparent',
          'circle-stroke-width': 2,
          'circle-stroke-color': '#111827',
          'circle-opacity': ['case', ['boolean', ['feature-state', 'selected'], false], 1, 0],
        },
      });

      setIsReady(true);
    });

    return () => {
      map.remove();
      mapRef.current = null;
      setIsReady(false);
    };
  }, [mapContainer, parks]);

  const runPerformanceTest = useCallback(async () => {
    const map = mapRef.current;

    if (!map || !isReady || isTesting) {
      return;
    }

    setIsTesting(true);
    setProgress(0);
    setCurrentRun(0);
    setResult(null);

    try {
      const summary = await runMapPerformanceTest({
        map,
        mode: 'geojson',
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
