import type { Difficulty, ParkFilter as ParkFilterType, PetStatus } from '../../types/park';
import { DIFFICULTY_OPTIONS } from '../../constants/difficulty';
import { PET_STATUS_OPTIONS } from '../../constants/petStatus';
import { Button } from './Button';
import { FilterChipGroup } from './FilterChipGroup';
import { DISTRICTS_OPTIONS } from '../../constants/districts';
import { useState } from 'react';

interface Props {
  filters: ParkFilterType;
  onChange: (filters: ParkFilterType) => void;
}

const districtOptions = DISTRICTS_OPTIONS.map((district) => ({
  value: district,
  label: district,
}));

const difficultyOptions = Object.entries(DIFFICULTY_OPTIONS).map(([value, item]) => ({
  value: value as Difficulty,
  label: item.label,
}));

const petStatusOptions = Object.entries(PET_STATUS_OPTIONS)
  .filter(([key]) => key !== 'unknown')
  .map(([value, item]) => ({
    value: value as PetStatus,
    label: item.label,
  }));

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

  const handleDistrict = (value: string) => {
    setTempFilters((prev) => ({
      ...prev,
      district: toggleValue(prev.district, value),
    }));
  };

  const handleReset = () => {
    const resetFilters = {
      difficulty: [],
      petStatus: [],
      district: [],
    };

    setTempFilters(resetFilters);
  };

  const handleApply = () => {
    onChange(tempFilters);
  };

  return (
    <div>
      <h2 className='text-xl font-bold'>필터</h2>

      <FilterChipGroup
        title='난이도'
        items={difficultyOptions}
        selectedValues={tempFilters.difficulty ?? []}
        onToggle={handleDifficulty}
      />

      <FilterChipGroup
        title='반려견 이용'
        items={petStatusOptions}
        selectedValues={tempFilters.petStatus ?? []}
        onToggle={handlePetStatus}
      />

      <FilterChipGroup
        title='지역'
        items={districtOptions}
        selectedValues={tempFilters.district ?? []}
        onToggle={handleDistrict}
      />

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
