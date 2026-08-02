import type { ReactNode } from 'react';

import { InfoCard } from './InfoCard';

interface ParkStat {
  icon?: ReactNode;
  label: string;
  value: string;
}

interface Props {
  stats: ParkStat[];
  variant?: 'card' | 'detail';
}

export const ParkStats = ({ stats, variant = 'detail' }: Props) => {
  return (
    <section className={variant === 'card' ? 'grid grid-cols-2 gap-3' : 'grid gap-4 md:grid-cols-4'}>
      {stats.map((stat) => (
        <InfoCard key={stat.label} icon={stat.icon} title={stat.label} value={stat.value} variant={variant} />
      ))}
    </section>
  );
};
