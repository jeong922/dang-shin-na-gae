import { Loader2 } from 'lucide-react';

interface Props {
  title?: string;
  description?: string;
}

export const LoadingOverlay = ({ title = '데이터를 불러오는 중', description = '잠시만 기다려주세요.' }: Props) => {
  return (
    <div className='absolute inset-0 flex items-center justify-center rounded-2xl bg-white/80 backdrop-blur-sm'>
      <div className='flex flex-col items-center gap-3'>
        <Loader2 className='animate-spin text-brand' size={32} />

        <div className='text-center'>
          <p className='font-semibold text-text-primary'>{title}</p>

          <p className='mt-1 text-sm text-text-muted'>{description}</p>
        </div>
      </div>
    </div>
  );
};
