import { X } from 'lucide-react';
import type { ParkFilter } from '../../types/park';
import { difficultyMap } from '../../utils/difficultyMap';
import { petStatusMap } from '../../utils/petStatusMap';

interface Props {
  filters: ParkFilter;
  onChange: (filters: ParkFilter) => void;
}

const getFilterLabel = (key: keyof ParkFilter, value: string) => {
  switch (key) {
    case 'difficulty':
      return difficultyMap[value as keyof typeof difficultyMap]?.label;

    case 'petStatus':
      return petStatusMap[value as keyof typeof petStatusMap]?.label;

    default:
      return value;
  }
};

export const ActiveFilters = ({ filters, onChange }: Props) => {
  const entries = Object.entries(filters);

  if (entries.length === 0) {
    return null;
  }

  const removeFilter = (key: keyof ParkFilter) => {
    onChange({
      ...filters,
      [key]: undefined,
    });
  };

  return (
    <div className='flex flex-wrap gap-2'>
      {entries.map(([key, value]) => {
        if (!value) return null;

        return (
          <button
            key={key}
            onClick={() => removeFilter(key as keyof ParkFilter)}
            className='flex items-center gap-1 cursor-pointer rounded-full bg-slate-100 px-3 py-1.5 text-sm text-text-primary transition hover:bg-slate-200'
          >
            {getFilterLabel(key as keyof ParkFilter, value)}

            <X size={14} />
          </button>
        );
      })}
    </div>
  );
};
