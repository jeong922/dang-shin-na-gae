import { SearchX } from 'lucide-react';
import { Button } from '../Button';

interface Props {
  title: string;
  description?: string;
  buttonText?: string;
  onAction?: () => void;
}

export const EmptyState = ({ title, description, buttonText = '이전으로', onAction }: Props) => {
  return (
    <section className='flex min-h-75 items-center justify-center px-6'>
      <div className='text-center'>
        <div className='mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-slate-100'>
          <SearchX size={32} className='text-text-muted' />
        </div>

        <h2 className='mt-5 text-xl font-bold text-text-primary'>{title}</h2>

        {description && <p className='mt-2 text-sm text-text-muted'>{description}</p>}

        {onAction && (
          <Button onClick={onAction} className='mt-6 px-6 text-sm'>
            {buttonText}
          </Button>
        )}
      </div>
    </section>
  );
};
