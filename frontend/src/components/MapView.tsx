import { useEffect, useRef } from 'react';
import { Map, NavigationControl } from 'maplibre-gl';

export const MapView = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<Map | null>(null);

  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    mapRef.current = new Map({
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

    mapRef.current.addControl(new NavigationControl(), 'top-right');

    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  return <div ref={mapContainer} className='h-[calc(100dvh-8rem)] overflow-hidden rounded-2xl border border-border' />;
};
