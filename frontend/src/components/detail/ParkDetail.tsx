import {
  Dog,
  ExternalLink,
  Leaf,
  MapPin,
  Maximize2,
  Mountain,
  Navigation,
  PawPrint,
  Phone,
  Trees,
  TrendingUp,
} from 'lucide-react';
import { useParams } from 'react-router';
import { usePark } from '../../hooks/usePark';
import { LoadingOverlay } from '../common/LoadingOverlay';
import { DIFFICULTY_OPTIONS } from '../../constants/difficulty';
import { PET_STATUS_OPTIONS } from '../../constants/petStatus';
import { formatArea, formatMeter, formatPercent } from '../../utils/format';
import { BackButton } from '../common/BackButton';
import { ParkStats } from '../common/ParkStats';
import { CardSection } from '../common/CardSection';
import { ContentCard } from '../common/ContentCard';
import { NoData } from '../common/NoData';
import { ImageWithFallback } from '../common/ImageWithFallback';
import { DifficultyBadge } from '../common/DifficultyBadge';
import { Badge } from '../common/Badge';
import { PetStatus } from '../common/PetStatus';

export const ParkDetail = () => {
  const { parkId } = useParams();

  const id = Number(parkId);

  const { park, isLoading, error } = usePark({ id });

  if (isLoading) {
    return <LoadingOverlay title='공원 정보를 불러오는 중' description='잠시만 기다려주세요.' />;
  }

  // TODO: UI 만들기
  if (error || !park) {
    return (
      <section className='mx-auto max-w-5xl py-20 text-center'>
        <h1 className='text-2xl font-bold'>공원을 찾을 수 없습니다.</h1>
      </section>
    );
  }

  const difficulty = DIFFICULTY_OPTIONS[park.difficulty.level];
  const petStatus = PET_STATUS_OPTIONS[park.pet.status];

  const parkStats = [
    {
      icon: <Maximize2 size={18} />,
      label: '면적',
      value: formatArea(park.information.area),
    },
    {
      icon: <TrendingUp size={18} />,
      label: '평균 경사도',
      value: formatPercent(park.difficulty.avgSlope),
    },
    {
      icon: <Mountain size={18} />,
      label: '고도 차이',
      value: `${formatMeter(park.difficulty.elevationDiff)}m`,
    },
    {
      icon: <PawPrint size={18} />,
      label: '반려견',
      value: petStatus.label,
    },
  ];

  return (
    <main className='mx-auto max-w-5xl space-y-8 px-6 py-8'>
      <BackButton label='목록으로' />

      <section>
        <div className='flex items-start justify-between'>
          <div>
            <h1 className='text-4xl font-bold'>{park.name}</h1>

            <div className='mt-3 flex items-center gap-2 text-sm text-text-muted'>
              <MapPin size={17} />
              {park.location.address}
            </div>
          </div>

          <DifficultyBadge difficulty={difficulty} />
        </div>
      </section>

      <section className='overflow-hidden rounded-3xl border border-border'>
        <ImageWithFallback src={park.images.image} alt={park.name} className='h-96 w-full object-cover' />
      </section>

      <ParkStats stats={parkStats} className='md:grid-cols-4' variant='detail' />

      <CardSection title='공원 소개'>
        <p className='whitespace-pre-line leading-8 text-text-secondary'>{park.description}</p>
      </CardSection>

      {park.images.map && (
        <CardSection icon={<MapPin size={20} />} title='공원 안내도'>
          <div className='overflow-hidden rounded-2xl border border-border bg-slate-50'>
            <ImageWithFallback
              src={park.images.map}
              alt={`${park.name} 안내도`}
              fallbackText='안내도가 제공되지 않습니다.'
              className='max-h-150 min-h-80 w-full object-contain'
            />
          </div>
        </CardSection>
      )}

      <CardSection icon={<Trees size={20} />} title='시설 안내'>
        {park.information.facilities.length > 0 ? (
          <div className='space-y-3'>
            {park.information.facilities.map((facility) => (
              <ContentCard key={facility.category} title={facility.category ?? '시설'}>
                {facility.content}
              </ContentCard>
            ))}
          </div>
        ) : (
          <NoData />
        )}
      </CardSection>

      <CardSection icon={<Leaf size={20} />} title='식물 정보'>
        {park.information.plants.length > 0 ? (
          <div className='space-y-3'>
            {park.information.plants.map((plant) => (
              <ContentCard
                key={plant.category}
                icon={<Leaf size={16} className='text-brand' />}
                title={plant.category ?? '식물'}
              >
                {plant.content}
              </ContentCard>
            ))}
          </div>
        ) : (
          <NoData />
        )}
      </CardSection>

      <CardSection icon={<PawPrint size={20} />} title='반려견 이용 안내'>
        <div className='mt-4 rounded-2xl bg-slate-50 p-4'>
          <PetStatus status={petStatus} />
        </div>

        {park.pet.notices.length > 0 && (
          <ul className='mt-4 space-y-2 text-sm leading-6 text-text-secondary'>
            {park.pet.notices.map((notice) => (
              <li key={notice}>• {notice}</li>
            ))}
          </ul>
        )}

        {park.pet.restrictedLocations.length > 0 && (
          <div className='mt-5'>
            <p className='text-sm font-semibold'>제한 구역</p>

            <div className='mt-2 flex flex-wrap gap-2'>
              {park.pet.restrictedLocations.map((location) => (
                <Badge key={location} className='bg-slate-100 text-text-primary shadow-sm'>
                  {location}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {park.pet.serviceAnimalAllowed && (
          <p className='mt-4 flex items-center gap-2 text-sm text-text-muted'>
            <Dog size={17} />
            안내견은 제한 구역에서도 출입 가능합니다.
          </p>
        )}
      </CardSection>

      <CardSection title='이용 안내'>
        {park.notices.length > 0 ? (
          <ul className='space-y-2 text-sm leading-7 text-text-secondary'>
            {park.notices.map((notice) => (
              <li key={notice}>• {notice}</li>
            ))}
          </ul>
        ) : (
          <NoData />
        )}
      </CardSection>

      <CardSection icon={<Navigation size={20} />} title='찾아오는 길'>
        {park.directions.length > 0 ? (
          <div className='space-y-3'>
            {park.directions.map((direction) => (
              <ContentCard
                key={direction.type}
                icon={<Navigation size={16} className='text-brand' />}
                title={direction.type ?? '이동 안내'}
              >
                {direction.content}
              </ContentCard>
            ))}
          </div>
        ) : (
          <NoData />
        )}
      </CardSection>

      <CardSection title='공원 정보'>
        <div className='space-y-3 text-text-secondary'>
          <p>관리기관 : {park.contact.department}</p>

          <p className='flex items-center gap-2'>
            <Phone size={16} />

            {park.contact.phone}
          </p>

          {park.contact.url && (
            <a href={park.contact.url} target='_blank' className='flex items-center gap-2 text-brand'>
              홈페이지 방문
              <ExternalLink size={16} />
            </a>
          )}
        </div>
      </CardSection>
    </main>
  );
};
