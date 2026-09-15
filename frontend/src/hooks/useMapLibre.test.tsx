import { act, useRef } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import type { FeatureCollection } from 'geojson';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import type { ParkMap } from '../types/park';
import { useMapLibre } from './useMapLibre';

interface MockSource {
  data: FeatureCollection;
  setData: (data: FeatureCollection) => void;
}

const mapState = vi.hoisted(() => ({
  load: undefined as (() => void) | undefined,
  sources: new Map<string, MockSource>(),
}));

vi.mock('@/lib/maplibre', () => ({ setupMapLibre: vi.fn() }));
vi.mock('maplibre-gl', () => ({
  Map: class {
    addControl = vi.fn();
    remove = vi.fn();
    addLayer = vi.fn();
    on(event: string, ...args: unknown[]) {
      if (event === 'load') mapState.load = args[0] as () => void;
    }
    getBounds() {
      return {
        getWest: () => 126.9,
        getSouth: () => 37.5,
        getEast: () => 127.1,
        getNorth: () => 37.6,
      };
    }
    addSource(id: string, options: { data: FeatureCollection | string }) {
      if (typeof options.data === 'string') return;
      const source: MockSource = {
        data: options.data,
        setData: vi.fn((data: FeatureCollection) => { source.data = data; }),
      };
      mapState.sources.set(id, source);
    }
    getSource(id: string) {
      return mapState.sources.get(id);
    }
  },
  NavigationControl: class {},
}));

const emptyParks: ParkMap[] = [];
const onSelectPark = vi.fn();
const onBoundsChange = vi.fn();
const park: ParkMap = {
  id: 1,
  name: '테스트 공원',
  lat: 37.5665,
  lon: 126.978,
  district: '종로구',
  area: 1000,
  difficulty: 'easy',
  avgSlope: 0.01,
  elevationDiff: 1,
  petStatus: 'allowed',
  petRestrictedLocations: [],
  serviceAnimalAllowed: false,
};

function Harness({ parks }: { parks: ParkMap[] }) {
  const mapContainer = useRef<HTMLDivElement>(null);
  useMapLibre({
    mapContainer,
    parks,
    searchResults: emptyParks,
    hasSearchCondition: false,
    selectedParkId: null,
    onSelectPark,
    onBoundsChange,
  });
  return <div ref={mapContainer} />;
}

describe('useMapLibre source initialization timing', () => {
  let container: HTMLDivElement;
  let root: Root;

  beforeEach(() => {
    vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true);
    mapState.sources.clear();
    mapState.load = undefined;
    vi.clearAllMocks();
    container = document.createElement('div');
    document.body.append(container);
    root = createRoot(container);
  });

  afterEach(async () => {
    await act(async () => root.unmount());
    container.remove();
    vi.unstubAllGlobals();
  });

  const render = async (parks: ParkMap[]) => {
    await act(async () => root.render(<Harness parks={parks} />));
  };
  const loadMap = async () => {
    expect(mapState.load).toBeTypeOf('function');
    await act(async () => mapState.load!());
  };
  const expectPoints = (parks: ParkMap[]) => {
    const source = mapState.sources.get('parks-source');
    expect(source).toBeDefined();
    expect(source!.data).toEqual({
      type: 'FeatureCollection',
      features: parks.map((park) => ({
        type: 'Feature',
        id: park.id,
        geometry: { type: 'Point', coordinates: [park.lon, park.lat] },
        properties: { difficulty: park.difficulty },
      })),
    });
  };

  it('updates an existing source when data arrives after load', async () => {
    await render(emptyParks);
    await loadMap();
    expectPoints(emptyParks);
    await render([park]);
    expectPoints([park]);
  });

  it('initializes the source with data that arrived before load', async () => {
    await render(emptyParks);
    await render([park]);
    expect(mapState.sources.has('parks-source')).toBe(false);
    await loadMap();
    expectPoints([park]);
  });

  it('uses the latest data when it changes multiple times before load', async () => {
    const latestPark = { ...park, id: 2, lon: 127.01, difficulty: 'hard' as const };
    await render(emptyParks);
    await render([park]);
    await render([latestPark]);
    await loadMap();
    expectPoints([latestPark]);
  });
});
