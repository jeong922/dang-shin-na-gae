import { useCallback, useState } from 'react';
import { MapView } from '../components/MapView';
import { ParkBottomSheet } from '../components/ParkBottomSheet';
import type { Park } from '../types/park';

export const HomePage = () => {
  const [selectedPark, setSelectedPark] = useState<Park | null>(null);

  const handleSelectPark = useCallback((park: Park) => {
    setSelectedPark(park);
  }, []);

  const onClose = () => {
    setSelectedPark(null);
  };

  return (
    <section className='relative h-[calc(100dvh-8rem)]'>
      <MapView onSelectPark={handleSelectPark} />
      <ParkBottomSheet park={selectedPark} onClose={onClose} />
    </section>
  );
};
