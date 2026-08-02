import { ChevronRight, Gauge, MapPin, Maximize2, Mountain, PawPrint, TrendingUp } from 'lucide-react';
import type { Park } from '../types/park';
import { difficultyMap } from '../utils/difficultyMap';
import { formatArea, formatMeter, formatPercent } from '../utils/format';
import { petStatusMap } from '../utils/petStatusMap';
import { useNavigate } from 'react-router';

interface Props {
  park: Park;
}

export const ParkCard = ({ park }: Props) => {
  const navigate = useNavigate();
  const difficulty = difficultyMap[park.difficulty];

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

      <div className='mt-6 grid grid-cols-2 gap-3'>
        <div className='rounded-2xl bg-slate-50 p-4'>
          <div className='flex items-center gap-2 text-text-muted'>
            <TrendingUp size={18} />
            <span className='text-xs'>평균 경사도</span>
          </div>

          <p className='mt-2 text-lg font-semibold'>{formatPercent(park.avgSlope)}</p>
        </div>

        <div className='rounded-2xl bg-slate-50 p-4'>
          <div className='flex items-center gap-2 text-text-muted'>
            <Mountain size={18} />
            <span className='text-xs'>고도 차이</span>
          </div>

          <p className='mt-2 text-lg font-semibold'>{formatMeter(park.elevationDiff)}m</p>
        </div>
      </div>

      <div className='mt-4 rounded-2xl bg-slate-50 p-4'>
        <div className='flex items-center gap-2 text-text-muted'>
          <Maximize2 size={18} />
          <p className='text-xs text-text-muted'>면적</p>
        </div>

        <p className='mt-1 text-lg font-semibold'>{formatArea(park.area)}</p>
      </div>

      <div className='mt-4 rounded-2xl bg-slate-50 p-4'>
        <div className='flex items-center justify-between'>
          <div className='flex items-center gap-2'>
            <PawPrint size={20} className='text-brand' />

            <p className='font-semibold text-text-primary'>반려견 이용</p>
          </div>

          <span className={`rounded-full px-3 py-1 text-sm font-semibold ${petStatusMap[park.petStatus].className}`}>
            {petStatusMap[park.petStatus].label}
          </span>
        </div>
      </div>

      <div className='mt-6 flex items-center justify-end text-brand font-medium'>
        상세 보기
        <ChevronRight size={18} className='ml-1 transition group-hover:translate-x-1' />
      </div>
    </article>
  );
};
