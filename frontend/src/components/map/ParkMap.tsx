import { useCallback, useState } from 'react';
import type { ParkMap as Map } from '../../types/park';
import { MapView } from './MapView';
import { BottomSheet } from '../ui/BottomSheet';
import { ParkDetailContent } from './ParkDetailContent';

export const ParkMap = () => {
  const [selectedPark, setSelectedPark] = useState<Map | null>(null);

  const handleSelectPark = useCallback((park: Map) => {
    setSelectedPark(park);
  }, []);

  const onClose = () => {
    setSelectedPark(null);
  };

  return (
    <section className='relative h-[calc(100dvh-8rem)]'>
      <MapView onSelectPark={handleSelectPark} />
      <BottomSheet open={!!selectedPark} onClose={onClose}>
        {selectedPark && <ParkDetailContent park={selectedPark} />}
      </BottomSheet>
    </section>
  );
};
