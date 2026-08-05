import { useState } from 'react';
import type { ParkFilter as ParkFilterType } from '../../types/park';
import { difficultyMap } from '../../utils/difficultyMap';
import { petStatusMap } from '../../utils/petStatusMap';
import { ChevronDown } from 'lucide-react';
import { Button } from './Button';

interface Props {
  filters: ParkFilterType;
  onChange: (filters: ParkFilterType) => void;
}

const districts = [
  '강남구',
  '강동구',
  '강북구',
  '강서구',
  '관악구',
  '광진구',
  '구로구',
  '금천구',
  '노원구',
  '도봉구',
  '동대문구',
  '동작구',
  '마포구',
  '서대문구',
  '서초구',
  '성동구',
  '성북구',
  '송파구',
  '양천구',
  '영등포구',
  '용산구',
  '은평구',
  '종로구',
  '중구',
  '중랑구',
] as const;

export const ParkFilter = ({ filters, onChange }: Props) => {
  const [tempFilters, setTempFilters] = useState<ParkFilterType>(filters);

  const handleDifficultyChange = (value: string) => {
    setTempFilters((prev) => ({
      ...prev,
      difficulty: prev.difficulty === value ? undefined : value,
    }));
  };

  const handlePetStatusChange = (value: string) => {
    setTempFilters((prev) => ({
      ...prev,
      petStatus: prev.petStatus === value ? undefined : value,
    }));
  };

  const handleReset = () => {
    setTempFilters({});
  };

  const handleApply = () => {
    onChange(tempFilters);
  };

  return (
    <div>
      <h2 className='text-xl font-bold'>필터</h2>

      {/* 난이도 */}
      <section className='mt-6'>
        <h3 className='text-sm font-semibold text-text-secondary'>난이도</h3>

        <div className='mt-3 flex flex-wrap gap-2'>
          {Object.entries(difficultyMap).map(([value, item]) => {
            const selected = tempFilters.difficulty === value;

            return (
              <button
                key={value}
                onClick={() => handleDifficultyChange(value)}
                className={`
                  rounded-full border px-4 py-2 text-sm transition cursor-pointer
                  ${selected ? 'border-brand bg-brand text-white' : 'border-border bg-white hover:bg-slate-50'}
                `}
              >
                {item.label}
              </button>
            );
          })}
        </div>
      </section>

      {/* 반려견 이용 */}
      <section className='mt-6'>
        <h3 className='text-sm font-semibold text-text-secondary'>반려견 이용</h3>

        <div className='mt-3 flex flex-wrap gap-2'>
          {Object.entries(petStatusMap)
            .filter(([key]) => key !== 'unknown')
            .map(([value, item]) => {
              const selected = tempFilters.petStatus === value;

              return (
                <button
                  key={value}
                  onClick={() => handlePetStatusChange(value)}
                  className={`
                    rounded-full border px-4 py-2 text-sm transition cursor-pointer
                    ${selected ? 'border-brand bg-brand text-white' : 'border-border bg-white hover:bg-slate-50'}
                  `}
                >
                  {item.label}
                </button>
              );
            })}
        </div>
      </section>

      {/* 지역 */}
      <section className='mt-6'>
        <h3 className='text-sm font-semibold text-text-secondary'>지역</h3>

        <div className='relative mt-3'>
          <select
            value={tempFilters.district ?? ''}
            onChange={(e) => setTempFilters((prev) => ({ ...prev, district: e.target.value || undefined }))}
            className='w-full appearance-none rounded-xl border border-border bg-white px-4 py-3 pr-10'
          >
            <option value=''>전체 지역</option>

            {districts.map((district) => (
              <option key={district} value={district}>
                {district}
              </option>
            ))}
          </select>

          <ChevronDown
            size={18}
            className='pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-text-muted'
          />
        </div>
      </section>

      <div className='mt-8 flex gap-3'>
        <Button variant='secondary' className='flex-1' onClick={handleReset}>
          초기화
        </Button>

        <Button variant='primary' className='flex-1' onClick={handleApply}>
          적용하기
        </Button>
      </div>
    </div>
  );
};
