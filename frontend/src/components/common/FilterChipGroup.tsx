interface Props<T extends string> {
  title: string;
  items: { value: T; label: string }[];
  selectedValues: T[];
  onToggle: (value: T) => void;
}

export const FilterChipGroup = <T extends string>({ title, items, selectedValues, onToggle }: Props<T>) => {
  return (
    <section className='mt-6'>
      <h3 className='text-sm font-semibold text-text-secondary'>{title}</h3>

      <div className='mt-3 flex flex-wrap gap-2'>
        {Object.entries(items).map(([key, item]) => {
          const value = key as T;
          const selected = selectedValues.includes(value);

          return (
            <button
              key={value}
              type='button'
              onClick={() => onToggle(value)}
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
