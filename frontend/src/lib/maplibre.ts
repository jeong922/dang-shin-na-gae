import { setWorkerUrl } from 'maplibre-gl';
import maplibreWorker from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';

export const setupMapLibre = () => {
  setWorkerUrl(maplibreWorker);
};
