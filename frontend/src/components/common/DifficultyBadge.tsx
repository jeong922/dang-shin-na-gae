import { Gauge } from 'lucide-react';
import { Badge } from './Badge';

interface Props {
  difficulty: {
    label: string;
    className: string;
  };
}

export const DifficultyBadge = ({ difficulty }: Props) => {
  return (
    <Badge className={`inline-flex items-center ${difficulty.className}`}>
      <Gauge size={15} className='mr-1' />
      {difficulty.label}
    </Badge>
  );
};
