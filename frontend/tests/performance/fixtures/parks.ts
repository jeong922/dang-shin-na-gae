import type { ParkMap } from '@/types/park';

const TEST_BOUNDS = {
  west: 126.85,
  south: 37.45,
  east: 127.1,
  north: 37.65,
};

export const createTestParks = (parks: ParkMap[], count: number): ParkMap[] => {
  if (parks.length === 0) return [];

  const columns = Math.ceil(Math.sqrt(count));
  const rows = Math.ceil(count / columns);

  return Array.from({ length: count }, (_, index) => {
    const source = parks[index % parks.length];

    const column = index % columns;
    const row = Math.floor(index / columns);

    const lon = TEST_BOUNDS.west + (column / Math.max(columns - 1, 1)) * (TEST_BOUNDS.east - TEST_BOUNDS.west);

    const lat = TEST_BOUNDS.south + (row / Math.max(rows - 1, 1)) * (TEST_BOUNDS.north - TEST_BOUNDS.south);

    return {
      ...source,
      id: index + 1,
      lon,
      lat,
    };
  });
};
