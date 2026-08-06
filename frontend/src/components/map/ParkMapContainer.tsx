import { lazy, Suspense, useCallback, useState } from 'react';
import type { ParkMap } from '../../types/park';
import { BottomSheet } from '../ui/BottomSheet';
import { ParkDetailContent } from './ParkDetailContent';

const MapView = lazy(() =>
  import('./MapView').then(({ MapView }) => ({
    default: MapView,
  })),
);

export const ParkMapContainer = () => {
  const [selectedPark, setSelectedPark] = useState<ParkMap | null>(null);

  const handleSelectPark = useCallback((park: ParkMap) => {
    setSelectedPark(park);
  }, []);

  const handleClose = useCallback(() => {
    setSelectedPark(null);
  }, []);

  return (
    <section className='relative h-[calc(100dvh-8rem)]'>
      <Suspense fallback={<div className='h-[calc(100dvh-8rem)] animate-pulse rounded-2xl bg-slate-100' />}>
        <MapView onSelectPark={handleSelectPark} />
      </Suspense>

      <BottomSheet open={!!selectedPark} onClose={handleClose}>
        {selectedPark && <ParkDetailContent park={selectedPark} />}
      </BottomSheet>
    </section>
  );
};
