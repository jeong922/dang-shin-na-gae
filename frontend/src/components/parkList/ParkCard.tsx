import { useNavigate } from 'react-router';
import type { Park } from '../../types/park';
import { difficultyMap } from '../../utils/difficultyMap';
import { ChevronRight, Gauge, MapPin, Maximize2, Mountain, TrendingUp } from 'lucide-react';
import { formatArea, formatMeter, formatPercent } from '../../utils/format';
import { ParkStats } from '../common/ParkStats';
import { petStatusMap } from '../../utils/petStatusMap';
import { PetStatus } from '../common/PetStatus';

interface Props {
  park: Park;
}

export const ParkCard = ({ park }: Props) => {
  const navigate = useNavigate();
  const difficulty = difficultyMap[park.difficulty];

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
      onClick={() => navigate(`/parks/${park.id}`)}
      className='group cursor-pointer rounded-3xl border border-border bg-white p-6 transition hover:-translate-y-1 hover:border-brand hover:shadow-lg'
    >
      <div className='flex items-start justify-between'>
        <div>
          <h2 className='text-xl font-bold'>{park.name}</h2>

          <div className='mt-2 flex items-center gap-1 text-sm text-text-muted'>
            <MapPin size={16} />
            {park.district}
          </div>
        </div>

        <span
          className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold ${difficulty.className}`}
        >
          <Gauge size={15} className='mr-1' />
          {difficulty.label}
        </span>
      </div>

      <ParkStats stats={stats} className='grid-cols-2 mt-6 gap-3' />

      <div className='mt-4 rounded-2xl bg-slate-50 p-4'>
        <PetStatus status={petStatusMap[park.petStatus]} />
      </div>

      <div className='mt-6 flex items-center justify-end text-brand font-medium'>
        상세 보기
        <ChevronRight size={18} className='ml-1 transition group-hover:translate-x-1' />
      </div>
    </article>
  );
};
