import { Search, SlidersHorizontal, X } from 'lucide-react';

interface Props {
  keyword: string;
  onKeywordChange: (value: string) => void;
  onFilterClick: () => void;
}

export const SearchBar = ({ keyword, onKeywordChange, onFilterClick }: Props) => {
  return (
    <div className='flex items-center gap-2 rounded-button border border-border bg-surface p-1.5'>
      <div className='flex min-w-0 flex-1 items-center gap-2 px-2 py-2'>
        <Search size={18} className='text-text-muted' />

        <input aria-label="공원 이름 검색"
          value={keyword}
          onChange={(e) => onKeywordChange(e.target.value)}
          placeholder='공원 이름을 검색하세요'
          className='min-w-0 flex-1 bg-transparent text-base placeholder:text-text-muted'
        />

        {keyword && (
          <button aria-label='검색어 지우기' onClick={() => onKeywordChange('')} className='rounded-full p-1 hover:bg-slate-200'>
            <X size={16} />
          </button>
        )}
      </div>

      <button aria-label="필터 열기" onClick={onFilterClick} className='rounded-button border border-border p-3 transition hover:bg-slate-100'>
        <SlidersHorizontal size={18} />
      </button>
    </div>
  );
};
