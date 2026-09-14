import type { Map as MapLibreMap } from 'maplibre-gl';

export type PerformanceTestMode = 'marker' | 'geojson';

export interface PerformanceTestResult {
  run: number;
  frames: number;
  fps: number;
  avgFrameTime: number;
  maxFrameTime: number;
  longTaskTime: number;
}

export interface PerformanceTestSummary {
  mode: PerformanceTestMode;
  pointCount: number;
  averageFps: number;
  averageFrameTime: number;
  averageMaxFrameTime: number;
  averageLongTaskTime: number;
  runs: PerformanceTestResult[];
}

interface RunPerformanceTestOptions {
  map: MapLibreMap;
  mode: PerformanceTestMode;
  pointCount: number;
  onProgress?: (current: number, total: number) => void;
}

const MOVE_DURATION = 1000;

const INITIAL_POSITION = {
  center: [126.978, 37.5665] as [number, number],
  zoom: 12,
};

const TEST_POSITIONS = [
  { center: [127.0276, 37.4979] as [number, number], zoom: 13 },
  { center: [126.9227, 37.5563] as [number, number], zoom: 14 },
  { center: [127.1058, 37.5145] as [number, number], zoom: 12 },
  { center: [126.9784, 37.5667] as [number, number], zoom: 15 },
  { center: [127.0474, 37.5172] as [number, number], zoom: 13 },
  { center: [126.8495, 37.5509] as [number, number], zoom: 12 },
  { center: [127.0558, 37.6542] as [number, number], zoom: 14 },
  { center: [126.9816, 37.4765] as [number, number], zoom: 13 },
  { center: [127.1238, 37.5384] as [number, number], zoom: 15 },
  { center: [126.9019, 37.5264] as [number, number], zoom: 12 },
];

const wait = (ms: number) =>
  new Promise<void>((resolve) => {
    window.setTimeout(resolve, ms);
  });

const waitForIdle = (map: MapLibreMap) =>
  new Promise<void>((resolve) => {
    if (map.loaded() && map.areTilesLoaded() && !map.isMoving()) {
      resolve();
      return;
    }

    map.once('idle', () => resolve());
  });

const warmUpMap = async (map: MapLibreMap) => {
  for (const position of TEST_POSITIONS) {
    map.jumpTo({
      center: position.center,
      zoom: position.zoom,
    });

    await waitForIdle(map);
  }

  map.jumpTo({
    center: INITIAL_POSITION.center,
    zoom: INITIAL_POSITION.zoom,
  });

  await waitForIdle(map);
  await wait(300);
};

const measureMovement = (
  map: MapLibreMap,
  run: number,
  position: (typeof TEST_POSITIONS)[number],
): Promise<PerformanceTestResult> =>
  new Promise((resolve) => {
    const frameTimes: number[] = [];

    let animationFrameId = 0;
    let previousFrameTime: number | null = null;
    let longTaskTime = 0;

    const longTaskObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        longTaskTime += entry.duration;
      }
    });

    try {
      longTaskObserver.observe({
        entryTypes: ['longtask'],
      });
    } catch {
      // Long Task API 미지원 브라우저
    }

    const measureFrame = (currentTime: number) => {
      if (previousFrameTime !== null) {
        frameTimes.push(currentTime - previousFrameTime);
      }

      previousFrameTime = currentTime;

      animationFrameId = requestAnimationFrame(measureFrame);
    };

    animationFrameId = requestAnimationFrame(measureFrame);

    map.easeTo({
      center: position.center,
      zoom: position.zoom,
      duration: MOVE_DURATION,
      essential: true,
    });

    map.once('moveend', () => {
      cancelAnimationFrame(animationFrameId);

      for (const entry of longTaskObserver.takeRecords()) {
        longTaskTime += entry.duration;
      }

      longTaskObserver.disconnect();

      const frames = frameTimes.length;

      const totalFrameTime = frameTimes.reduce((sum, frameTime) => sum + frameTime, 0);

      const avgFrameTime = frames > 0 ? totalFrameTime / frames : 0;

      const maxFrameTime = frames > 0 ? Math.max(...frameTimes) : 0;

      const fps = avgFrameTime > 0 ? 1000 / avgFrameTime : 0;

      resolve({
        run,
        frames,
        fps,
        avgFrameTime,
        maxFrameTime,
        longTaskTime,
      });
    });
  });

export const runMapPerformanceTest = async ({
  map,
  mode,
  pointCount,
  onProgress,
}: RunPerformanceTestOptions): Promise<PerformanceTestSummary> => {
  onProgress?.(0, TEST_POSITIONS.length);

  await warmUpMap(map);

  const results: PerformanceTestResult[] = [];

  for (let i = 0; i < TEST_POSITIONS.length; i += 1) {
    const result = await measureMovement(map, i + 1, TEST_POSITIONS[i]);

    results.push(result);

    onProgress?.(i + 1, TEST_POSITIONS.length);

    // 각 테스트 사이에 잠깐 안정화
    await wait(300);
  }

  const average = (values: number[]) => values.reduce((sum, value) => sum + value, 0) / values.length;

  const summary: PerformanceTestSummary = {
    mode,
    pointCount,
    averageFps: average(results.map((result) => result.fps)),
    averageFrameTime: average(results.map((result) => result.avgFrameTime)),
    averageMaxFrameTime: average(results.map((result) => result.maxFrameTime)),
    averageLongTaskTime: average(results.map((result) => result.longTaskTime)),
    runs: results,
  };

  console.table(results);

  console.table({
    mode,
    pointCount,
    averageFps: summary.averageFps,
    averageFrameTime: summary.averageFrameTime,
    averageMaxFrameTime: summary.averageMaxFrameTime,
    averageLongTaskTime: summary.averageLongTaskTime,
  });

  return summary;
};
