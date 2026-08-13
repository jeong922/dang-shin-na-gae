from pydantic import BaseModel


class ParkLocation(BaseModel):
    lat: float
    lon: float
    district: str
    address: str


class ParkFacility(BaseModel):
    category: str | None
    content: str


class ParkPlant(BaseModel):
    category: str | None
    content: str


class ParkInformation(BaseModel):
    area: float
    openedAt: str
    facilities: list[ParkFacility]
    plants: list[ParkPlant]


class ParkDifficulty(BaseModel):
    level: str
    avgSlope: float
    elevationDiff: float


class ParkPet(BaseModel):
    status: str
    notices: list[str]
    restrictedLocations: list[str]
    serviceAnimalAllowed: bool


class ParkDirection(BaseModel):
    type: str
    content: str


class ParkContact(BaseModel):
    department: str
    phone: str
    url: str


class ParkImages(BaseModel):
    image: str
    map: str


class ParkListItem(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    difficulty: str
    avgSlope: float
    elevationDiff: float
    area: float
    district: str
    petStatus: str


class ParkDetailResponse(BaseModel):
    id: int
    name: str
    description: str
    location: ParkLocation
    information: ParkInformation
    difficulty: ParkDifficulty
    pet: ParkPet
    notices: list[str]
    directions: list[ParkDirection]
    contact: ParkContact
    images: ParkImages


class ParkMapItem(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    difficulty: str
    avgSlope: float
    elevationDiff: float
    area: float
    district: str
    petStatus: str
    petRestrictedLocations: list[str]
    serviceAnimalAllowed: bool


class ParkMapResponse(BaseModel):
    items: list[ParkMapItem]
    total: int


class ParkListResponse(BaseModel):
    items: list[ParkListItem]
    page: int
    pageSize: int
    total: int
    totalPages: int


class ParkSearchResponse(BaseModel):
    items: list[ParkMapResponse]
    total: int
