import type { ReactNode } from 'react';

interface Props {
  children: ReactNode;
  className?: string;
}

export const Overlay = ({ children, className = '' }: Props) => {
  return (
    <div
      className={`absolute inset-0 z-10 flex items-center justify-center rounded-2xl bg-white/80 backdrop-blur-sm ${className}`}
    >
      {children}
    </div>
  );
};
