import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary';
}

export const Button = ({ children, variant = 'primary', className = '', ...props }: Props) => {
  const variantClass = {
    primary: 'bg-brand text-white hover:opacity-90',
    secondary: 'border border-border bg-white hover:bg-slate-50',
  };

  return (
    <button
      className={`rounded-xl py-3 font-semibold transition cursor-pointer ${variantClass[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};
