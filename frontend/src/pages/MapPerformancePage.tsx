import { useState } from 'react';

import { useMapParks } from '@/hooks/useMapParks';
import { MapPerformanceTest } from '@/tests/performance/MapPerformanceTest';

type TestMode = 'marker' | 'geojson';

const SEOUL_BOUNDS = {
  west: 126.6,
  south: 37.3,
  east: 127.3,
  north: 37.8,
};

const MapPerformancePage = () => {
  const [mode, setMode] = useState<TestMode>('marker');
  const [count, setCount] = useState(132);

  const { parks, total, isLoading, isFetching, error } = useMapParks(SEOUL_BOUNDS);

  if (isLoading) {
    return <div>테스트 데이터를 불러오는 중...</div>;
  }

  if (error) {
    return <div>공원 데이터를 불러오지 못했습니다.</div>;
  }

  return (
    <div className='p-6'>
      <div className='mb-4'>
        <p>
          원본 데이터: {parks.length}개 / 전체 {total}개
        </p>

        {isFetching && <p>데이터 갱신 중...</p>}
      </div>

      <div className='mb-4 flex gap-2'>
        <button type='button' onClick={() => setMode('marker')}>
          Marker
        </button>

        <button type='button' onClick={() => setMode('geojson')}>
          GeoJSON
        </button>

        {[132, 500, 1000].map((value) => (
          <button key={value} type='button' onClick={() => setCount(value)}>
            {value}
          </button>
        ))}
      </div>

      <MapPerformanceTest key={`${mode}-${count}`} parks={parks} count={count} mode={mode} />
    </div>
  );
};

export default MapPerformancePage;
