import { createContext, useContext } from 'react';

export const ParkCompareContext = createContext<{
  ids: number[];
  toggle: (id: number, name: string) => void;
} | null>(null);

export const useParkCompare = () => {
  const context = useContext(ParkCompareContext);
  if (!context) throw new Error('ParkCompareProvider가 필요합니다.');
  return context;
};
