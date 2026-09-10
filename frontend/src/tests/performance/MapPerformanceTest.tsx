import { useMemo, useRef } from 'react';

import type { ParkMap } from '@/types/park';
import { createTestParks } from './parks';
import type { PerformanceTestSummary } from './runMapPerformanceTest';
import { useGeoJSONPerformanceTest } from './useGeoJSONPerformanceTest';
import { useMarkerPerformanceTest } from './useMarkerPerformanceTest';

type TestMode = 'marker' | 'geojson';

interface Props {
  parks: ParkMap[];
  count: number;
  mode: TestMode;
}

interface PerformancePanelProps {
  mode: TestMode;
  count: number;
  mapContainer: React.RefObject<HTMLDivElement | null>;
  isReady: boolean;
  isTesting: boolean;
  progress: number;
  currentRun: number;
  totalRuns: number;
  result: PerformanceTestSummary | null;
  onRun: () => void;
}

export const MapPerformanceTest = ({ parks, count, mode }: Props) => {
  if (mode === 'marker') {
    return <MarkerPerformanceTest parks={parks} count={count} />;
  }

  return <GeoJSONPerformanceTest parks={parks} count={count} />;
};

const MarkerPerformanceTest = ({ parks, count }: Omit<Props, 'mode'>) => {
  const mapContainer = useRef<HTMLDivElement>(null);

  const testParks = useMemo(() => createTestParks(parks, count), [parks, count]);

  const { isReady, isTesting, progress, currentRun, totalRuns, result, runPerformanceTest } = useMarkerPerformanceTest({
    mapContainer,
    parks: testParks,
  });

  return (
    <PerformancePanel
      mode='marker'
      count={count}
      mapContainer={mapContainer}
      isReady={isReady}
      isTesting={isTesting}
      progress={progress}
      currentRun={currentRun}
      totalRuns={totalRuns}
      result={result}
      onRun={runPerformanceTest}
    />
  );
};

const GeoJSONPerformanceTest = ({ parks, count }: Omit<Props, 'mode'>) => {
  const mapContainer = useRef<HTMLDivElement>(null);

  const testParks = useMemo(() => createTestParks(parks, count), [parks, count]);

  const { isReady, isTesting, progress, currentRun, totalRuns, result, runPerformanceTest } = useGeoJSONPerformanceTest(
    {
      mapContainer,
      parks: testParks,
    },
  );

  return (
    <PerformancePanel
      mode='geojson'
      count={count}
      mapContainer={mapContainer}
      isReady={isReady}
      isTesting={isTesting}
      progress={progress}
      currentRun={currentRun}
      totalRuns={totalRuns}
      result={result}
      onRun={runPerformanceTest}
    />
  );
};

const PerformancePanel = ({
  mode,
  count,
  mapContainer,
  isReady,
  isTesting,
  progress,
  currentRun,
  totalRuns,
  result,
  onRun,
}: PerformancePanelProps) => {
  const modeLabel = mode === 'marker' ? 'DOM Marker' : 'GeoJSON Layer';

  return (
    <section>
      <div className='mb-4 rounded-xl border border-gray-200 bg-white p-5'>
        <div className='flex flex-wrap items-center justify-between gap-4'>
          <div>
            <p className='text-sm text-gray-500'>현재 테스트</p>

            <h2 className='mt-1 text-xl font-semibold text-gray-900'>
              {modeLabel} · {count.toLocaleString()} Points
            </h2>
          </div>

          <div className='flex items-center gap-2 text-sm'>
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                isTesting ? 'bg-amber-500' : isReady ? 'bg-green-500' : 'bg-gray-300'
              }`}
            />

            <span className='text-gray-600'>{isTesting ? '테스트 중' : isReady ? '준비 완료' : '지도 준비 중'}</span>
          </div>
        </div>

        <button
          type='button'
          disabled={!isReady || isTesting}
          onClick={onRun}
          className='mt-5 rounded-lg bg-gray-900 px-5 py-3 text-sm font-medium text-white transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-40'
        >
          {isTesting ? '성능 측정 중...' : '▶ 테스트 시작'}
        </button>

        {isTesting && (
          <div className='mt-5'>
            <div className='mb-2 flex items-center justify-between text-sm'>
              <span className='font-medium text-gray-700'>성능 측정 중</span>

              <span className='text-gray-500'>
                {currentRun} / {totalRuns}회 · {Math.round(progress)}%
              </span>
            </div>

            <div className='h-2 overflow-hidden rounded-full bg-gray-200'>
              <div className='h-full bg-gray-900 transition-[width] duration-300' style={{ width: `${progress}%` }} />
            </div>

            {currentRun === 0 && (
              <p className='mt-2 text-xs text-gray-500'>지도 타일을 준비하고 워밍업하는 중입니다.</p>
            )}
          </div>
        )}
      </div>

      <div className='overflow-hidden rounded-xl border border-gray-200 bg-gray-100'>
        <div ref={mapContainer} className='h-162.5 w-full' />
      </div>

      {result && (
        <div className='mt-4'>
          <div className='mb-3 flex items-center justify-between'>
            <h3 className='font-semibold text-gray-900'>테스트 결과</h3>

            <span className='text-sm text-gray-500'>10회 평균</span>
          </div>

          <div className='grid grid-cols-2 gap-3 lg:grid-cols-4'>
            <ResultCard label='Average FPS' value={result.averageFps.toFixed(1)} />

            <ResultCard label='Avg Frame Time' value={`${result.averageFrameTime.toFixed(1)} ms`} />

            <ResultCard label='Max Frame Time' value={`${result.averageMaxFrameTime.toFixed(1)} ms`} />

            <ResultCard label='Long Task' value={`${result.averageLongTaskTime.toFixed(1)} ms`} />
          </div>
        </div>
      )}
    </section>
  );
};

interface ResultCardProps {
  label: string;
  value: string;
}

const ResultCard = ({ label, value }: ResultCardProps) => {
  return (
    <div className='rounded-xl border border-gray-200 bg-white p-4'>
      <p className='text-xs font-medium text-gray-500'>{label}</p>

      <p className='mt-1 text-xl font-semibold text-gray-900'>{value}</p>
    </div>
  );
};
