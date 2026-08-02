import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router';

interface Props {
  label?: string;
}

export const BackButton = ({ label = '뒤로가기' }: Props) => {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate(-1)}
      className='flex cursor-pointer items-center gap-2 text-sm text-text-muted transition hover:text-brand'
    >
      <ArrowLeft size={18} />
      {label}
    </button>
  );
};
