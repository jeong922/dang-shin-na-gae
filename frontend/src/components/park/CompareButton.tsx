import { useParkCompare } from '../../hooks/useParkCompare';
import { Button } from '../ui/Button';
import { Check } from 'lucide-react';

export const CompareButton = ({
  id,
  name,
  className = '',
}: {
  id: number;
  name: string;
  className?: string;
}) => {
  const { ids, toggle } = useParkCompare();
  const selected = ids.includes(id);
  return (
    <Button
      variant='secondary'
      className={`inline-flex items-center justify-center gap-2 ${className}`}
      aria-pressed={selected}
      aria-label={`${name} ${selected ? '비교에서 빼기' : '비교에 담기'}`}
      onClick={() => toggle(id, name)}
    >
      {selected && <Check size={16} aria-hidden='true' className='shrink-0' />}
      <span>{selected ? '비교에서 빼기' : '비교에 담기'}</span>
    </Button>
  );
};
