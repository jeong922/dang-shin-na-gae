interface Props {
  children: React.ReactNode;
  className?: string;
}

export const Badge = ({ children, className = '' }: Props) => {
  return <span className={`rounded-button px-2 py-1 text-caption font-medium ${className}`}>{children}</span>;
};
