interface Props {
  children: React.ReactNode;
  className?: string;
}

export const Badge = ({ children, className = '' }: Props) => {
  return <span className={`rounded-full px-3 py-1 text-sm font-semibold ${className}`}>{children}</span>;
};
