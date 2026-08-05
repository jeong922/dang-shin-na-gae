import { Dog, MapPin, Maximize2, Mountain, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router';
import type { ParkMap } from '../../types/park';
import { formatArea, formatMeter, formatPercent } from '../../utils/format';
import { difficultyMap } from '../../utils/difficultyMap';
import { petStatusMap } from '../../utils/petStatusMap';
import { Guide } from '../guide/Guide';
import { ParkStats } from '../common/ParkStats';
import { DifficultyBadge } from '../common/DifficultyBadge';
import { Badge } from '../common/Badge';
import { PetStatus } from '../common/PetStatus';
import { Button } from '../common/Button';

interface Props {
  park: ParkMap;
}

export const ParkDetailContent = ({ park }: Props) => {
  const navigate = useNavigate();

  const stats = [
    {
      icon: <Maximize2 size={18} />,
      label: '면적',
      value: formatArea(park.area),
    },
    {
      icon: <TrendingUp size={18} />,
      label: '평균 경사도',
      value: formatPercent(park.avgSlope),
    },
    {
      icon: <Mountain size={18} />,
      label: '고도 차이',
      value: `${formatMeter(park.elevationDiff)}m`,
    },
  ];

  return (
    <>
      <div className='relative flex min-h-20 items-start justify-between'>
        <div className='pr-20'>
          <h2 className='text-xl font-bold text-text-primary'>{park.name}</h2>

          <div className='mt-2 flex items-center gap-1.5 text-sm text-text-muted'>
            <MapPin size={15} className='shrink-0' />
            <span>{park.district}</span>
          </div>
        </div>

        <div className='absolute right-0 top-12'>
          <DifficultyBadge difficulty={difficultyMap[park.difficulty]} />
        </div>
      </div>

      <div className='mt-4'>
        <ParkStats stats={stats} className='grid-cols-2 gap-3' />
      </div>

      <div className='mt-4 rounded-2xl bg-slate-50 p-4'>
        <PetStatus status={petStatusMap[park.petStatus]} />

        {park.petRestrictedLocations.length > 0 && (
          <div className='mt-3'>
            <p className='text-sm text-text-muted'>출입 제한 구역</p>

            <div className='mt-2 flex flex-wrap gap-2'>
              {park.petRestrictedLocations.map((location) => (
                <Badge key={location} className='text-text-primary shadow-sm'>
                  {location}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {park.serviceAnimalAllowed && (
          <div className='mt-3 flex items-center gap-2 rounded-xl bg-white px-3 py-2 text-sm text-text-muted'>
            <Dog size={16} className='shrink-0 text-brand' />
            <span>안내견은 제한 구역에서도 출입 가능합니다.</span>
          </div>
        )}
      </div>

      <Guide />

      <Button variant='primary' className='mt-4 w-full' onClick={() => navigate(`/parks/${park.id}`)}>
        상세보기
      </Button>
    </>
  );
};
