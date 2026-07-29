export type Difficulty = 'easy' | 'medium' | 'hard' | 'expert';

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
  difficulty: 'easy' | 'medium' | 'hard' | 'expert';
  avgSlope: number;
  elevationDiff: number;
  petStatus: 'allowed' | 'restricted' | 'prohibited' | 'unknown';
  petRestrictedLocations: string[];
  serviceAnimalAllowed: boolean;
}

export interface ParkMapResponse {
  items: Park[];
  total: number;
}
