import { PawPrint } from 'lucide-react';
import { PetStatusBadge } from './PetStatusBadge';

interface Props {
  status: {
    label: string;
    className: string;
  };
}

export const PetStatus = ({ status }: Props) => {
  return (
    <div className='flex flex-wrap items-center justify-between gap-2'>
      <div className='flex items-center gap-2'>
        <PawPrint size={16} className='text-brand' />
        <p className='text-sm font-medium text-text-primary'>반려견 이용</p>
      </div>
      <PetStatusBadge status={status} />
    </div>
  );
};
