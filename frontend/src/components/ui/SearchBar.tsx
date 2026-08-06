import { Search, SlidersHorizontal, X } from 'lucide-react';

interface Props {
  keyword: string;
  onKeywordChange: (value: string) => void;
  onFilterClick: () => void;
}

export const SearchBar = ({ keyword, onKeywordChange, onFilterClick }: Props) => {
  return (
    <div className='flex items-center gap-3 rounded-2xl border border-border bg-white p-2 shadow-md'>
      <div className='flex flex-1 items-center gap-2 rounded-xl bg-slate-50 px-3 py-2'>
        <Search size={18} className='text-text-muted' />

        <input
          value={keyword}
          onChange={(e) => onKeywordChange(e.target.value)}
          placeholder='공원 이름을 검색하세요'
          className='flex-1 bg-transparent outline-none placeholder:text-text-muted'
        />

        {keyword && (
          <button onClick={() => onKeywordChange('')} className='rounded-full p-1 hover:bg-slate-200'>
            <X size={16} />
          </button>
        )}
      </div>

      <button onClick={onFilterClick} className='rounded-xl border border-border p-3 transition hover:bg-slate-100'>
        <SlidersHorizontal size={18} />
      </button>
    </div>
  );
};
