import { X } from 'lucide-react';
import type { ParkFilter } from '../../types/park';
import { difficultyMap } from '../../constants/difficulty';
import { petStatusMap } from '../../constants/petStatus';

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
  const removeFilter = (key: keyof ParkFilter, value: string) => {
    const currentValues = filters[key] ?? [];

    const nextValues = currentValues.filter((item) => item !== value);

    onChange({
      ...filters,
      [key]: nextValues,
    });
  };

  const entries = Object.entries(filters) as [keyof ParkFilter, string[] | undefined][];

  if (entries.every(([, values]) => !values || values.length === 0)) {
    return null;
  }

  return (
    <div className='flex flex-wrap gap-2'>
      {entries.map(([key, values]) => {
        if (!values) return null;

        return values.map((value) => (
          <button
            key={`${key}-${value}`}
            type='button'
            onClick={() => removeFilter(key as keyof ParkFilter, value)}
            className='flex items-center gap-1 cursor-pointer rounded-full bg-slate-100 px-3 py-1.5 text-sm text-text-primary transition hover:bg-slate-200'
          >
            {getFilterLabel(key as keyof ParkFilter, value)}

            <X size={14} />
          </button>
        ));
      })}
    </div>
  );
};
