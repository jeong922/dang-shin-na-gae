import { TriangleAlert } from 'lucide-react';
import { Button } from '../Button';

interface Props {
  title?: string;
  description?: string;
  buttonText?: string;
  onRetry?: () => void;
}

export const ErrorState = ({
  title = '문제가 발생했습니다.',
  description = '잠시 후 다시 시도해주세요.',
  buttonText = '다시 시도',
  onRetry,
}: Props) => {
  return (
    <section className='flex min-h-100 items-center justify-center px-6'>
      <div className='text-center'>
        <div className='mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-50'>
          <TriangleAlert size={32} className='text-red-500' />
        </div>

        <h2 className='mt-5 text-xl font-bold text-text-primary'>{title}</h2>

        <p className='mt-2 text-sm text-text-muted'>{description}</p>

        {onRetry && (
          <Button onClick={onRetry} className='mt-6 px-6 text-sm'>
            {buttonText}
          </Button>
        )}
      </div>
    </section>
  );
};
