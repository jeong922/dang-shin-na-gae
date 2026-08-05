interface FilterItem<T> {
  value: T;
  label: string;
}

interface Props<T> {
  title: string;
  items: FilterItem<T>[];
  selectedValues: T[];
  onToggle: (value: T) => void;
}

export const FilterChipGroup = <T,>({ title, items, selectedValues, onToggle }: Props<T>) => {
  return (
    <section className='mt-6'>
      <h3 className='text-sm font-semibold text-text-secondary'>{title}</h3>

      <div className='mt-3 flex flex-wrap gap-2'>
        {items.map((item) => {
          const selected = selectedValues.includes(item.value);

          return (
            <button
              key={String(item.value)}
              type='button'
              onClick={() => onToggle(item.value)}
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
  );
};
