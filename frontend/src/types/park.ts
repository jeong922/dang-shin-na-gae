export type Difficulty = 'easy' | 'medium' | 'hard' | 'expert';
export type PetStatus = 'allowed' | 'restricted' | 'prohibited' | 'unknown';

// export interface Park {
//   id: number;
//   name: string;
//   district: string;
//   lat: number;
//   lon: number;
//   area: number;
//   avgElevation: number;
//   minElevation: number;
//   maxElevation: number;
//   elevationDiff: number;
//   avgSlope: number;
//   areaScore: number;
//   elevationScore: number;
//   slopeScore: number;
//   difficultyScore: number;
//   difficulty: Difficulty;
// }

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
  petRestrictedLocations: string[];
  serviceAnimalAllowed: boolean;
}

export interface ParksResponse {
  items: Park[];
  total: number;
}

export interface ParkListResponse extends ParksResponse {
  page: number;
  pageSize: number;
  totalPages: number;
}

export type ParkMapResponse = ParksResponse;
