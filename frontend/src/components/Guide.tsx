import { useState } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { ChevronDown } from 'lucide-react';

export const Guide = () => {
  const [showGuide, setShowGuide] = useState(false);

  return (
    <div className='mt-5 overflow-hidden rounded-2xl border border-border'>
      <button
        onClick={() => setShowGuide((prev) => !prev)}
        className='flex w-full items-center justify-between bg-slate-50 px-4 py-3'
      >
        <span className='font-medium text-text-primary'>ⓘ 난이도 계산 기준</span>

        <motion.div
          animate={{
            rotate: showGuide ? 180 : 0,
          }}
          transition={{
            duration: 0.2,
          }}
        >
          <ChevronDown size={18} />
        </motion.div>
      </button>

      <AnimatePresence initial={false}>
        {showGuide && (
          <motion.div
            initial={{
              height: 0,
              opacity: 0,
            }}
            animate={{
              height: 'auto',
              opacity: 1,
            }}
            exit={{
              height: 0,
              opacity: 0,
            }}
            transition={{
              duration: 0.25,
            }}
            className='overflow-hidden'
          >
            <div className='space-y-4 border-t border-border p-4 text-sm text-text-muted'>
              <div>
                <p className='font-semibold text-text-primary'>📏 면적 (30%)</p>
                <p>공원의 전체 면적입니다. 넓은 공원일수록 오래 산책할 수 있어 체력 소진에 유리합니다.</p>
              </div>

              <div>
                <p className='font-semibold text-text-primary'>📈 평균 경사도 (30%)</p>
                <p>공원 주변 여러 지점의 고도 데이터를 활용해 산책 시 느껴지는 경사도를 추정했습니다.</p>
              </div>

              <div>
                <p className='font-semibold text-text-primary'>🏔️ 고도 차이 (40%)</p>
                <p>주변 샘플 지점 간 고도 차이를 반영해 오르내림 정도를 계산했습니다.</p>
              </div>

              <div className='rounded-xl bg-white p-3'>
                <p className='font-semibold text-text-primary'>💡 최종 난이도</p>

                <p className='mt-1'>세 가지 요소를 정규화한 뒤 가중치를 적용하여 난이도를 계산했습니다.</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
