interface Props {
  icon?: React.ReactNode;
  title: string;
  value: string;
  variant?: 'card' | 'detail';
}

export const InfoCard = ({ icon, title, value, variant = 'detail' }: Props) => {
  return (
    <div className={variant === 'card' ? 'p-4 rounded-2xl bg-slate-50' : 'p-5'}>
      <div className='flex items-center gap-2 text-sm text-text-muted'>
        {icon}

        <span>{title}</span>
      </div>

      <p className='mt-2 text-lg font-semibold'>{value}</p>
    </div>
  );
};
