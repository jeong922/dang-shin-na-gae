import { useEffect, useRef } from 'react';
import { Map, NavigationControl, Marker } from 'maplibre-gl';
import type { Park } from '../types/park';
import { useMapParks } from '../hooks/useMapParks';
import { LoadingOverlay } from './LoadingOverlay';
import { ErrorOverlay } from './ErrorOverlay';

interface Props {
  onSelectPark: (park: Park) => void;
}

export const MapView = ({ onSelectPark }: Props) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<Map | null>(null);

  const { parks, isLoading, error, refetch } = useMapParks();

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    const map = new Map({
      container: mapContainer.current,
      style: 'https://tiles.openfreemap.org/styles/bright',
      center: [126.978, 37.5665],
      zoom: 11,
      minZoom: 10,
      maxZoom: 18,
      maxBounds: [
        [126.7, 37.4],
        [127.2, 37.72],
      ],
    });

    map.addControl(
      new NavigationControl({
        showCompass: false,
      }),
      'top-right',
    );

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current || !parks) return;

    parks.forEach((park: Park) => {
      const marker = new Marker().setLngLat([park.lon, park.lat]).addTo(mapRef.current!);

      marker.getElement().addEventListener('click', () => {
        onSelectPark(park);
      });
    });
  }, [parks, onSelectPark]);

  return (
    <div className='relative'>
      <div ref={mapContainer} className='h-[calc(100dvh-8rem)] overflow-hidden rounded-2xl border border-border' />

      {isLoading && <LoadingOverlay title='공원 정보를 불러오는 중' description='잠시만 기다려주세요.' />}

      {error && (
        <ErrorOverlay
          title='공원 정보를 불러올 수 없습니다.'
          description={`서버와 연결할 수 없습니다.\n잠시 후 다시 시도해주세요.`}
          onRetry={refetch}
        />
      )}
    </div>
  );
};
