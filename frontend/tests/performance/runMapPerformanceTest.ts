import type { Map as MapLibreMap } from 'maplibre-gl';

export interface PerformanceTestResult {
  run: number;
  frames: number;
  fps: number;
  avgFrameTime: number;
  maxFrameTime: number;
  longTaskTime: number;
}

const TEST_RUNS = 10;

// 한 번의 지도 이동 시간
const MOVE_DURATION = 1000;

// 이동이 끝난 후 잠시 안정화
const WAIT_AFTER_MOVE = 300;

// 테스트 시작 전 대기
const INITIAL_WAIT = 1000;

/**
 * 실제 데이터가 있는 서울 영역 안에서 이동
 *
 * 너무 넓게 이동하지 않고,
 * 서로 다른 방향으로 조금씩 움직이도록 구성
 */
const TEST_POSITIONS: Array<{
  center: [number, number];
  zoom: number;
}> = [
  {
    center: [126.95, 37.52],
    zoom: 12,
  },
  {
    center: [126.98, 37.52],
    zoom: 12,
  },
  {
    center: [127.01, 37.52],
    zoom: 12,
  },
  {
    center: [127.04, 37.55],
    zoom: 12,
  },
  {
    center: [127.01, 37.58],
    zoom: 12,
  },
  {
    center: [126.98, 37.58],
    zoom: 12,
  },
  {
    center: [126.95, 37.58],
    zoom: 12,
  },
  {
    center: [126.92, 37.55],
    zoom: 12,
  },
  {
    center: [126.95, 37.55],
    zoom: 12,
  },
  {
    center: [126.98, 37.55],
    zoom: 12,
  },
];

const wait = (ms: number) => {
  return new Promise<void>((resolve) => {
    setTimeout(resolve, ms);
  });
};

/**
 * 지도 이동
 */
const moveMap = (map: MapLibreMap, center: [number, number], zoom: number) => {
  return new Promise<void>((resolve) => {
    const handleMoveEnd = () => {
      resolve();
    };

    map.once('moveend', handleMoveEnd);

    map.easeTo({
      center,
      zoom,
      duration: MOVE_DURATION,
      essential: true,
    });
  });
};

/**
 * requestAnimationFrame 기반 프레임 측정
 */
const createFrameMeasurement = () => {
  let running = true;

  let frameCount = 0;

  let lastFrameTime = performance.now();

  let totalFrameTime = 0;
  let maxFrameTime = 0;

  const frameLoop = (time: number) => {
    if (!running) return;

    const frameTime = time - lastFrameTime;

    if (frameTime > 0) {
      totalFrameTime += frameTime;
      maxFrameTime = Math.max(maxFrameTime, frameTime);
      frameCount++;
    }

    lastFrameTime = time;

    requestAnimationFrame(frameLoop);
  };

  requestAnimationFrame(frameLoop);

  return {
    stop: () => {
      running = false;

      const avgFrameTime = frameCount > 0 ? totalFrameTime / frameCount : 0;

      return {
        frameCount,
        avgFrameTime,
        maxFrameTime,
      };
    },
  };
};

export const runMapPerformanceTest = async (map: MapLibreMap): Promise<PerformanceTestResult[]> => {
  const results: PerformanceTestResult[] = [];

  console.group('🚀 Map Performance Test');

  console.log(`테스트 횟수: ${TEST_RUNS}`);
  console.log(`지도 이동 시간: ${MOVE_DURATION}ms`);
  console.log(`이동 후 대기: ${WAIT_AFTER_MOVE}ms`);

  // ============================================================
  // Long Task Observer
  // ============================================================

  let longTaskTime = 0;

  const observer =
    typeof PerformanceObserver !== 'undefined'
      ? new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            longTaskTime += entry.duration;
          }
        })
      : null;

  observer?.observe({
    entryTypes: ['longtask'],
  });

  // ============================================================
  // 초기 위치
  // ============================================================

  const firstPosition = TEST_POSITIONS[0];

  map.jumpTo({
    center: firstPosition.center,
    zoom: firstPosition.zoom,
  });

  await wait(INITIAL_WAIT);

  // ============================================================
  // 10회 반복
  // ============================================================

  for (let run = 0; run < TEST_RUNS; run++) {
    const target = TEST_POSITIONS[run];

    console.log(`\n▶ Run ${run + 1}/${TEST_RUNS}`, target.center);

    // 이전 Long Task 값 제거
    longTaskTime = 0;

    // 프레임 측정 시작
    const frameMeasurement = createFrameMeasurement();

    const startTime = performance.now();

    // 지도 이동
    await moveMap(map, target.center, target.zoom);

    const endTime = performance.now();

    // 프레임 측정 종료
    const frameResult = frameMeasurement.stop();

    const elapsed = endTime - startTime;

    const fps = elapsed > 0 ? (frameResult.frameCount / elapsed) * 1000 : 0;

    const result: PerformanceTestResult = {
      run: run + 1,
      frames: frameResult.frameCount,
      fps,
      avgFrameTime: frameResult.avgFrameTime,
      maxFrameTime: frameResult.maxFrameTime,
      longTaskTime,
    };

    results.push(result);

    console.table({
      FPS: Number(fps.toFixed(2)),
      Frames: frameResult.frameCount,
      'Avg Frame Time (ms)': Number(frameResult.avgFrameTime.toFixed(2)),
      'Max Frame Time (ms)': Number(frameResult.maxFrameTime.toFixed(2)),
      'Long Task (ms)': Number(longTaskTime.toFixed(2)),
    });

    // 다음 이동 전에 잠시 대기
    await wait(WAIT_AFTER_MOVE);
  }

  observer?.disconnect();

  // ============================================================
  // 평균 계산
  // ============================================================

  const average = {
    fps: results.reduce((sum, result) => sum + result.fps, 0) / results.length,

    frames: results.reduce((sum, result) => sum + result.frames, 0) / results.length,

    avgFrameTime: results.reduce((sum, result) => sum + result.avgFrameTime, 0) / results.length,

    maxFrameTime: results.reduce((sum, result) => sum + result.maxFrameTime, 0) / results.length,

    longTaskTime: results.reduce((sum, result) => sum + result.longTaskTime, 0) / results.length,
  };

  // ============================================================
  // 최종 결과
  // ============================================================

  console.log('\n====================================');
  console.log('📊 최종 평균 결과');
  console.log('====================================');

  console.table({
    'Average FPS': Number(average.fps.toFixed(2)),

    'Average Frames': Number(average.frames.toFixed(2)),

    'Average Frame Time (ms)': Number(average.avgFrameTime.toFixed(2)),

    'Average Max Frame Time (ms)': Number(average.maxFrameTime.toFixed(2)),

    'Average Long Task (ms)': Number(average.longTaskTime.toFixed(2)),
  });

  console.log('====================================');

  console.groupEnd();

  return results;
};
