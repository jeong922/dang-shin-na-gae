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
    <div className='absolute inset-0 flex items-center justify-center rounded-2xl bg-white/90 backdrop-blur-sm'>
      <div className='mx-6 max-w-sm rounded-2xl border border-red-200 bg-white p-6 text-center shadow-lg'>
        <TriangleAlert className='mx-auto mb-3 text-red-500' size={40} />

        <h3 className='font-semibold text-text-primary'>{title}</h3>

        <p className='mt-2 whitespace-pre-line text-sm text-text-muted'>{description}</p>

        {onRetry && (
          <button
            onClick={onRetry}
            className='mt-5 w-full cursor-pointer rounded-xl bg-brand px-4 py-2.5 font-semibold text-white transition hover:opacity-90 active:scale-[0.98]'
          >
            {buttonText}
          </button>
        )}
      </div>
    </div>
  );
};
