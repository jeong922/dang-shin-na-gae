import { type ReactNode, type MouseEvent } from 'react';
import { AnimatePresence, motion } from 'motion/react';

interface Props {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
}

export const BottomSheet = ({ open, onClose, children }: Props) => {
  const handleOverlayClick = (e: MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {open && (
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

            {children}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
