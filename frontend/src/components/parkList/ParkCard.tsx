import { useNavigate } from 'react-router';
import type { Park } from '../../types/park';
import { DIFFICULTY_OPTIONS } from '../../constants/difficulty';
import { ChevronRight, Gauge, MapPin, Maximize2, Mountain, TrendingUp } from 'lucide-react';
import { formatArea, formatMeter, formatPercent } from '../../utils/format';
import { ParkStats } from '../park/ParkStats';
import { PET_STATUS_OPTIONS } from '../../constants/petStatus';
import { PetStatus } from '../park/PetStatus';

interface Props {
  park: Park;
}

export const ParkCard = ({ park }: Props) => {
  const navigate = useNavigate();
  const difficulty = DIFFICULTY_OPTIONS[park.difficulty];

  const stats = [
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
    {
      icon: <Maximize2 size={18} />,
      label: '면적',
      value: formatArea(park.area),
    },
  ];

  return (
    <article
      role='link' tabIndex={0}
      onKeyDown={(event) => { if (event.key === 'Enter') navigate(`/parks/${park.id}`); }}
      onClick={() => navigate(`/parks/${park.id}`)}
      className='group cursor-pointer rounded-card border border-border bg-surface p-4 sm:p-5 transition-colors hover:border-slate-400 hover:bg-slate-50/50'
    >
      <div className='flex flex-wrap items-start justify-between gap-3'>
        <div>
          <h2 className='text-title font-semibold tracking-tight'>{park.name}</h2>

          <div className='mt-2 flex items-center gap-1 text-sm text-text-muted'>
            <MapPin size={16} />
            {park.district}
          </div>
        </div>

        <span
          className={`inline-flex items-center rounded-button px-2 py-1 text-caption font-medium ${difficulty.className}`}
        >
          <Gauge size={15} className='mr-1' />
          {difficulty.label}
        </span>
      </div>

      <ParkStats stats={stats} className='grid-cols-2 sm:grid-cols-3 mt-4 gap-x-4 gap-y-2' />

      <div className='mt-4 border-t border-border pt-4'>
        <PetStatus status={PET_STATUS_OPTIONS[park.petStatus]} />
      </div>

      <div className='mt-4 flex items-center justify-end text-brand font-medium'>
        상세 보기
        <ChevronRight size={18} className='ml-1 ' />
      </div>
    </article>
  );
};
