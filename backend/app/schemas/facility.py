from datetime import date
from uuid import UUID

from pydantic import BaseModel


class FacilityMapItem(BaseModel):
    facilityId: UUID
    name: str
    facilityType: str
    lat: float
    lon: float
    distanceMeters: float
    allowedPetSize: str | None
    petRestrictions: str | None
    indoor: str | None
    outdoor: str | None
    openingHours: str | None


class FacilityListItem(FacilityMapItem):
    roadAddress: str | None
    lotAddress: str | None
    allowedPetSize: str | None
    petRestrictions: str | None
    indoor: str | None
    outdoor: str | None


class FacilityMapResponse(BaseModel):
    items: list[FacilityMapItem]
    total: int


class FacilityListResponse(BaseModel):
    items: list[FacilityListItem]
    page: int
    pageSize: int
    total: int
    totalPages: int


class FacilityDetailResponse(BaseModel):
    facilityId: UUID
    name: str
    businessCategory: str
    facilityCategory: str
    facilityType: str
    city: str
    district: str
    neighborhood: str | None
    lat: float
    lon: float
    roadAddress: str | None
    lotAddress: str | None
    phone: str | None
    website: str | None
    closedDays: str | None
    openingHours: str | None
    parkingAvailable: str | None
    admissionFee: str | None
    petExclusive: str | None
    allowedPetSize: str | None
    petRestrictions: str | None
    petExtraFee: str | None
    indoor: str | None
    outdoor: str | None
    description: str | None
    recordUpdatedAt: date | None
