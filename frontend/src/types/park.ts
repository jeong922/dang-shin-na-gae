export type Difficulty = 'easy' | 'medium' | 'hard' | 'expert';

export type PetStatus = 'allowed' | 'restricted' | 'prohibited' | 'unknown';

export type DirectionType = '도보' | '버스' | '셔틀버스' | '지하철' | '자동차' | '기타';

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

export interface ParkDetail {
  id: number;
  name: string;
  description: string;
  location: {
    lat: number;
    lon: number;
    district: string;
    address: string;
  };
  information: {
    area: number;
    openedAt: string;
    facilities: Facility[];
    plants: Plant[];
  };
  difficulty: {
    level: Difficulty;
    avgSlope: number;
    elevationDiff: number;
  };
  pet: {
    status: PetStatus;
    notices: string[];
    restrictedLocations: string[];
    serviceAnimalAllowed: boolean;
  };
  notices: string[];
  directions: Direction[];
  contact: {
    department: string;
    phone: string;
    url: string;
  };

  images: {
    image: string;
    map: string;
  };
}

export interface ParkFilter {
  difficulty?: string;
  district?: string;
  petStatus?: string;
}

export interface Facility {
  category: string | null;
  content: string;
}

export interface Plant {
  category: string | null;
  content: string;
}

export interface Direction {
  type: string | null;
  content: string;
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
