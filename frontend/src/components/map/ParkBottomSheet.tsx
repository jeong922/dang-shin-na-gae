import { type MouseEvent } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Dog, MapPin, Maximize2, Mountain, TrendingUp, X } from 'lucide-react';
import type { ParkMap } from '../../types/park';
import { formatArea, formatMeter, formatPercent } from '../../utils/format';
import { difficultyMap } from '../../utils/difficultyMap';
import { Guide } from '../guide/Guide';
import { petStatusMap } from '../../utils/petStatusMap';
import { useNavigate } from 'react-router';
import { ParkStats } from '../common/ParkStats';
import { DifficultyBadge } from '../common/DifficultyBadge';
import { Badge } from '../common/Badge';
import { PetStatus } from '../common/PetStatus';

interface Props {
  park: ParkMap | null;
  onClose: () => void;
}

export const ParkBottomSheet = ({ park, onClose }: Props) => {
  const navigate = useNavigate();
  const handleOverlayClick = (e: MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (!park) return null;

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

            <div className='relative flex min-h-20 items-start justify-between'>
              <div className='pr-20'>
                <h2 className='text-xl font-bold text-text-primary'>{park.name}</h2>

                <div className='mt-2 flex items-center gap-1.5 text-sm text-text-muted'>
                  <MapPin size={15} className='shrink-0' />
                  <span>{park.district}</span>
                </div>
              </div>

              <button
                onClick={onClose}
                className='absolute right-0 top-0 cursor-pointer rounded-full p-2 text-text-muted transition hover:bg-gray-100'
              >
                <X size={20} />
              </button>

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

            <button
              className='mt-4 w-full cursor-pointer rounded-xl bg-brand py-3 font-semibold text-white transition hover:opacity-90'
              onClick={() => navigate(`parks/${park.id}`)}
            >
              상세 보기
            </button>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
