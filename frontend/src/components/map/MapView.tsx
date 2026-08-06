import { useCallback, useEffect, useRef, useState } from 'react';
import { Map as MapLibreMap, NavigationControl, Marker } from 'maplibre-gl';
import type { ParkMap } from '../../types/park';
import { useMapParks } from '../../hooks/useMapParks';
import { LoadingOverlay } from '../ui/loading/LoadingOverlay';
import { useDebounce } from '../../hooks/useDebounce';
import { Overlay } from '../ui/Overlay';
import { ErrorState } from '../ui/error/ErrorState';

interface Props {
  onSelectPark: (park: ParkMap) => void;
}

interface Bounds {
  west: number;
  south: number;
  east: number;
  north: number;
}

export const MapView = ({ onSelectPark }: Props) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);

  const markersRef = useRef<Map<number, Marker>>(new Map());

  const [bounds, setBounds] = useState<Bounds | null>(null);

  const debouncedBounds = useDebounce(bounds, 500);

  const { parks, isLoading, isFetching, error, refetch } = useMapParks({
    ...(debouncedBounds ?? {}),
  });

  const updateMarkers = useCallback(() => {
    if (!mapRef.current) return;

    const currentParkIds = new Set<number>();

    parks.forEach((park) => {
      currentParkIds.add(park.id);

      if (markersRef.current.has(park.id)) {
        return;
      }

      const marker = new Marker().setLngLat([park.lon, park.lat]).addTo(mapRef.current!);

      const element = marker.getElement() as HTMLElement;
      element.style.cursor = 'pointer';

      element.onclick = () => {
        onSelectPark(park);
      };

      markersRef.current.set(park.id, marker);
    });

    markersRef.current.forEach((marker, id) => {
      if (!currentParkIds.has(id)) {
        marker.remove();
        markersRef.current.delete(id);
      }
    });
  }, [parks, onSelectPark]);

  useEffect(() => {
    updateMarkers();
  }, [updateMarkers]);

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

    map.on('load', updateBounds);
    map.on('moveend', updateBounds);

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

  return (
    <div className='relative h-[calc(100dvh-8rem)]'>
      <div ref={mapContainer} className='h-full overflow-hidden rounded-2xl border border-border' />

      {isLoading && parks.length === 0 && (
        <LoadingOverlay title='공원 정보를 불러오는 중' description='잠시만 기다려주세요.' />
      )}

      {isFetching && parks.length > 0 && (
        <div className='absolute right-4 top-4 rounded-lg bg-white px-3 py-2 text-sm shadow'>업데이트 중...</div>
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
