import type { ReactNode } from 'react';

interface Props {
  icon?: ReactNode;
  title: string;
  children: ReactNode;
}

export const ContentCard = ({ icon, title, children }: Props) => {
  return (
    <div className='border-l-2 border-border pl-4 py-1'>
      <div className='flex items-center gap-2'>
        {icon}

        <p className='font-semibold'>{title}</p>
      </div>

      <div className='mt-2 text-sm leading-7 text-text-secondary'>{children}</div>
    </div>
  );
};
