import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary';
}

export const Button = ({ children, variant = 'primary', className = '', ...props }: Props) => {
  const variantClass = {
    primary: 'bg-brand text-white hover:bg-brand-hover',
    secondary: 'border border-border bg-white hover:bg-slate-50',
  };

  return (
    <button
      className={`rounded-button min-h-11 px-4 py-2.5 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${variantClass[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};
