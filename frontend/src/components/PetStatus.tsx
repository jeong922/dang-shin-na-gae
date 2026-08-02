import { PawPrint } from 'lucide-react';
import { PetStatusBadge } from './common/PetStatusBadge';

interface Props {
  status: {
    label: string;
    className: string;
  };
}

export const PetStatus = ({ status }: Props) => {
  return (
    <div className='flex items-center justify-between'>
      <div className='flex items-center gap-2'>
        <PawPrint size={20} className='text-brand' />
        <p className='font-semibold text-text-primary'>반려견 이용</p>
      </div>
      <PetStatusBadge status={status} />
    </div>
  );
};
