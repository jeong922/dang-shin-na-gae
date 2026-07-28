import { ChevronRight, Gauge, MapPin, Mountain, TrendingUp } from 'lucide-react';
import type { Park } from '../types/park';

interface Props {
  park: Park;
}

const difficultyMap = {
  easy: {
    label: '쉬움',
    className: 'bg-level-easy/10 text-level-easy',
  },
  medium: {
    label: '보통',
    className: 'bg-level-medium/10 text-level-medium',
  },
  hard: {
    label: '어려움',
    className: 'bg-level-hard/10 text-level-hard',
  },
  expert: {
    label: '매우 어려움',
    className: 'bg-level-expert/10 text-level-expert',
  },
} as const;

export const ParkCard = ({ park }: Props) => {
  const difficulty = difficultyMap[park.difficulty];

  return (
    <article
      key={park.id}
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

          <p className='mt-2 text-lg font-semibold'>{park.avgSlope}%</p>
        </div>

        <div className='rounded-2xl bg-slate-50 p-4'>
          <div className='flex items-center gap-2 text-text-muted'>
            <Mountain size={18} />
            <span className='text-xs'>고도 차이</span>
          </div>

          <p className='mt-2 text-lg font-semibold'>{park.elevationDiff}m</p>
        </div>
      </div>

      <div className='mt-4 rounded-2xl bg-slate-50 p-4'>
        <p className='text-xs text-text-muted'>면적</p>

        <p className='mt-1 text-lg font-semibold'>{park.area.toLocaleString()}㎡</p>
      </div>

      <div className='mt-6 flex items-center justify-end text-brand font-medium'>
        상세 보기
        <ChevronRight size={18} className='ml-1 transition group-hover:translate-x-1' />
      </div>
    </article>
  );
};
