import type { ReactNode } from 'react';

import { InfoCard } from './InfoCard';

interface ParkStat {
  icon?: ReactNode;
  label: string;
  value: string;
}

interface Props {
  stats: ParkStat[];
  className?: string;
  variant?: 'card' | 'detail';
}

export const ParkStats = ({ stats, className, variant = 'card' }: Props) => {
  return (
    <section className={`grid gap-4 ${className}`}>
      {stats.map((stat) => (
        <InfoCard key={stat.label} icon={stat.icon} title={stat.label} value={stat.value} variant={variant} />
      ))}
    </section>
  );
};
