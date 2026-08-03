import type { ParkMap } from '../../types/park';
import { BottomSheet } from '../common/BottomSheet';
import { ParkDetailContent } from './ParkDetailContent';

interface Props {
  park: ParkMap | null;
  onClose: () => void;
}

export const ParkBottomSheet = ({ park, onClose }: Props) => {
  return (
    <BottomSheet open={!!park} onClose={onClose}>
      {park && <ParkDetailContent park={park} onClose={onClose} />}
    </BottomSheet>
  );
};
