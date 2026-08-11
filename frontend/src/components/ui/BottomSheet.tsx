import { type MouseEvent, type ReactNode, useEffect } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { X } from 'lucide-react';

interface Props {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  variant?: 'map' | 'filter';
}

export const BottomSheet = ({ open, onClose, children, variant = 'map' }: Props) => {
  const positionClass =
    variant === 'filter'
      ? 'fixed bottom-20 left-4 right-4 mx-auto w-[calc(100%-2rem)] max-w-[61rem]'
      : 'absolute bottom-4 left-4 right-4';

  const overlayClass = variant === 'filter' ? 'fixed inset-0 bg-black/10' : 'absolute inset-0 bg-black/10';

  const handleOverlayClick = (e: MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // BottomSheet가 열려 있는 동안 배경 스크롤 방지
  useEffect(() => {
    if (!open) return;

    const originalOverflow = document.body.style.overflow;

    document.body.style.overflow = 'hidden';

    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, [open]);

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Overlay */}
          <motion.div
            className={`${overlayClass} z-40`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={handleOverlayClick}
          />

          {/* BottomSheet */}
          <motion.div
            className={`${positionClass} z-50 max-h-[calc(100dvh-5rem)] overflow-hidden rounded-3xl border border-border bg-white/95 p-5 shadow-xl backdrop-blur-md`}
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
            dragConstraints={{
              top: 0,
              bottom: 0,
            }}
            dragElastic={0.25}
            dragMomentum={false}
            onDragEnd={(_, info) => {
              if (info.offset.y > 40 || info.velocity.y > 250) {
                onClose();
              }
            }}
          >
            {/* 닫기 버튼 */}
            <button
              onClick={onClose}
              className='absolute right-4 top-4 rounded-full p-2 text-text-muted transition hover:bg-gray-100'
              aria-label='닫기'
            >
              <X size={20} />
            </button>

            {/* Drag Handle */}
            <div className='mb-4 flex shrink-0 justify-center'>
              <motion.div
                className='h-1.5 w-12 rounded-full bg-gray-300'
                whileHover={{ scaleX: 1.1 }}
                whileTap={{
                  scaleX: 1.2,
                  scaleY: 1.3,
                }}
                transition={{ duration: 0.15 }}
              />
            </div>

            {/* Content */}
            <div className='max-h-[calc(100dvh-9rem)] overflow-y-auto'>{children}</div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
