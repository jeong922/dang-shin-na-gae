import { type MouseEvent } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Gauge, MapPin, Maximize2, Mountain, TrendingUp, X } from 'lucide-react';
import type { Park } from '../types/park';
import { formatArea, formatMeter, formatPercent } from '../utils/format';
import { difficultyMap } from '../utils/difficultyMap';
import { Guide } from './Guide';

interface Props {
  park: Park | null;
  onClose: () => void;
}

export const ParkBottomSheet = ({ park, onClose }: Props) => {
  const handleOverlayClick = (e: MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {park && (
        <>
          <motion.div
            className='absolute inset-0 z-10 bg-black/10'
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={handleOverlayClick}
          />

          <motion.div
            className='absolute bottom-4 left-4 right-4 z-20 rounded-3xl border border-border bg-white/95 p-5 shadow-xl backdrop-blur-md'
            initial={{ y: '120%', opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: '120%', opacity: 0 }}
            transition={{
              type: 'spring',
              stiffness: 380,
              damping: 34,
              mass: 0.8,
            }}
            drag='y'
            dragDirectionLock
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={0.25}
            dragMomentum={false}
            onDragEnd={(_, info) => {
              if (info.offset.y > 40 || info.velocity.y > 250) {
                onClose();
              }
            }}
          >
            <div className='mb-4 flex justify-center'>
              <motion.div
                className='h-1.5 w-12 rounded-full bg-gray-300'
                whileHover={{ scaleX: 1.1 }}
                whileTap={{ scaleX: 1.2, scaleY: 1.3 }}
                transition={{ duration: 0.15 }}
              />
            </div>

            <div className='flex items-start justify-between'>
              <div>
                <h2 className='text-xl font-bold text-text-primary'>{park.name}</h2>

                <div className='mt-2 flex items-center gap-1.5 text-sm text-text-muted'>
                  <MapPin size={15} className='shrink-0' />
                  <span>{park.district}</span>
                </div>
              </div>

              <button
                onClick={onClose}
                className='cursor-pointer rounded-full p-2 text-text-muted transition hover:bg-gray-100'
              >
                <X size={20} />
              </button>
            </div>

            <div className='mt-4'>
              <span
                className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold ${difficultyMap[park.difficulty].className}`}
              >
                <Gauge size={16} className='mr-1' />
                난이도 {difficultyMap[park.difficulty].label}
              </span>
            </div>

            <div className='mt-4 grid grid-cols-2 gap-3'>
              <div className='flex items-center gap-3 rounded-2xl bg-slate-50 p-3'>
                <Maximize2 size={20} className='text-brand' />

                <div>
                  <p className='text-xs text-text-muted'>면적</p>
                  <p className='font-semibold'>{formatArea(park.area)}</p>
                </div>
              </div>

              <div className='flex items-center gap-3 rounded-2xl bg-slate-50 p-3'>
                <TrendingUp size={20} className='text-brand' />

                <div>
                  <p className='text-xs text-text-muted'>평균 경사도</p>
                  <p className='font-semibold'>{formatPercent(park.avgSlope)}</p>
                </div>
              </div>

              <div className='flex items-center gap-3 rounded-2xl bg-slate-50 p-3'>
                <Mountain size={20} className='text-brand' />

                <div>
                  <p className='text-xs text-text-muted'>고도 차이</p>
                  <p className='font-semibold'>{formatMeter(park.elevationDiff)}m</p>
                </div>
              </div>
            </div>

            <Guide />

            <button className='mt-4 w-full cursor-pointer rounded-xl bg-brand py-3 font-semibold text-white transition hover:opacity-90'>
              상세 보기
            </button>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
