import type { ReactNode } from 'react';

interface Props {
  title: string;
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
}

export const CardSection = ({ title, icon, children, className = '' }: Props) => {
  return (
    <section className={`rounded-3xl border border-border bg-white p-6 ${className}`}>
      <div className='mb-5 flex items-center gap-2'>
        {icon}

        <h2 className='text-xl font-bold'>{title}</h2>
      </div>

      {children}
    </section>
  );
};
