export type Difficulty = 'easy' | 'medium' | 'hard' | 'expert';
export type PetStatus = 'allowed' | 'restricted' | 'prohibited' | 'unknown';

export interface Park {
  id: number;
  name: string;
  lat: number;
  lon: number;
  district: string;
  area: number;
  difficulty: Difficulty;
  avgSlope: number;
  elevationDiff: number;
  petStatus: PetStatus;
}

export interface ParkMap extends Park {
  petRestrictedLocations: string[];
  serviceAnimalAllowed: boolean;
}

export interface ParksResponse<T> {
  items: T[];
  total: number;
}

export interface ParkListResponse extends ParksResponse<Park> {
  page: number;
  pageSize: number;
  totalPages: number;
}

export type ParkMapResponse = ParksResponse<ParkMap>;
