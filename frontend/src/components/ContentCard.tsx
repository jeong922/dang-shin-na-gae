import type { ReactNode } from 'react';

interface Props {
  icon?: ReactNode;
  title: string;
  children: ReactNode;
}

export const ContentCard = ({ icon, title, children }: Props) => {
  return (
    <div className='rounded-2xl bg-slate-50 p-4'>
      <div className='flex items-center gap-2'>
        {icon}

        <p className='font-semibold'>{title}</p>
      </div>

      <div className='mt-2 text-sm leading-7 text-text-secondary'>{children}</div>
    </div>
  );
};
