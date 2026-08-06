import { Badge } from '../ui/Badge';

interface Props {
  status: {
    label: string;
    className: string;
  };
}

export const PetStatusBadge = ({ status }: Props) => {
  return <Badge className={status.className}>{status.label}</Badge>;
};
