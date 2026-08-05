import { useState } from 'react';
import type { Difficulty, ParkFilter as ParkFilterType, PetStatus } from '../../types/park';
import { difficultyMap } from '../../utils/difficultyMap';
import { petStatusMap } from '../../utils/petStatusMap';
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

type District = (typeof districts)[number];

export const ParkFilter = ({ filters, onChange }: Props) => {
  const [tempFilters, setTempFilters] = useState<ParkFilterType>({
    difficulty: filters.difficulty ?? [],
    petStatus: filters.petStatus ?? [],
    district: filters.district ?? [],
  });

  const toggleValue = <T,>(values: T[] = [], value: T) => {
    return values.includes(value) ? values.filter((item) => item !== value) : [...values, value];
  };

  const handleDifficulty = (value: Difficulty) => {
    setTempFilters((prev) => ({
      ...prev,
      difficulty: toggleValue(prev.difficulty, value),
    }));
  };

  const handlePetStatus = (value: PetStatus) => {
    setTempFilters((prev) => ({
      ...prev,
      petStatus: toggleValue(prev.petStatus, value),
    }));
  };

  const handleDistrict = (value: District) => {
    setTempFilters((prev) => ({
      ...prev,
      district: toggleValue(prev.district, value),
    }));
  };

  const handleReset = () => {
    setTempFilters({
      difficulty: [],
      petStatus: [],
      district: [],
    });
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
          {Object.entries(difficultyMap).map(([key, item]) => {
            const value = key as Difficulty;

            const selected = tempFilters.difficulty?.includes(value) ?? false;

            return (
              <button
                key={value}
                type='button'
                onClick={() => handleDifficulty(value)}
                className={`rounded-full border px-4 py-2 text-sm transition cursor-pointer ${
                  selected ? 'border-brand bg-brand text-white' : 'border-border bg-white hover:bg-slate-50'
                }`}
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
            .map(([key, item]) => {
              const value = key as PetStatus;

              const selected = tempFilters.petStatus?.includes(value) ?? false;

              return (
                <button
                  key={value}
                  type='button'
                  onClick={() => handlePetStatus(value)}
                  className={`rounded-full border px-4 py-2 text-sm transition cursor-pointer ${
                    selected ? 'border-brand bg-brand text-white' : 'border-border bg-white hover:bg-slate-50'
                  }`}
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

        <div className='mt-3 flex flex-wrap gap-2'>
          {districts.map((district) => {
            const selected = tempFilters.district?.includes(district) ?? false;

            return (
              <button
                key={district}
                type='button'
                onClick={() => handleDistrict(district)}
                className={`rounded-full border px-4 py-2 text-sm transition cursor-pointer ${
                  selected ? 'border-brand bg-brand text-white' : 'border-border bg-white hover:bg-slate-50'
                }`}
              >
                {district}
              </button>
            );
          })}
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
