import { TriangleAlert } from 'lucide-react';

interface Props {
  title?: string;
  description?: string;
  buttonText?: string;
  onRetry?: () => void;
}

export const ErrorOverlay = ({
  title = '데이터를 불러올 수 없습니다.',
  description = '잠시 후 다시 시도해주세요.',
  buttonText = '다시 시도',
  onRetry,
}: Props) => {
  return (
    <div className='absolute inset-0 flex items-center justify-center rounded-2xl bg-white/80 backdrop-blur-sm'>
      <div className='mx-6 max-w-sm rounded-3xl border border-border bg-white p-8 text-center shadow-sm'>
        <div className='mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-red-50'>
          <TriangleAlert className='text-red-500' size={28} />
        </div>

        <h3 className='mt-5 text-lg font-bold text-text-primary'>{title}</h3>

        <p className='mt-2 text-sm leading-6 text-text-muted'>{description}</p>

        {onRetry && (
          <button
            onClick={onRetry}
            className='mt-6 w-full rounded-xl bg-brand px-4 py-3 text-sm font-semibold text-white transition hover:opacity-90 active:scale-[0.98]'
          >
            {buttonText}
          </button>
        )}
      </div>
    </div>
  );
};
