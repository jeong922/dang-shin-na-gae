import { useEffect, useState, type ReactNode } from 'react';
import { useQueries } from '@tanstack/react-query';
import { getPark } from '../api/park';
import { ParkCompareContext } from '../hooks/useParkCompare';

export const ParkCompareProvider = ({ children }: { children: ReactNode }) => {
  const [selection, setSelection] = useState<{
    ids: number[];
    message: string;
  }>({ ids: [], message: '' });
  useEffect(() => {
    if (!selection.message) return;
    const timer = setTimeout(
      () => setSelection((previous) => ({ ...previous, message: '' })),
      5000,
    );
    return () => clearTimeout(timer);
  }, [selection]);

  // 상세 화면과 동일한 Query 키로 데이터를 미리 준비한다. UI 상태에는 ID만 보관한다.
  useQueries({
    queries: selection.ids.map((id) => ({
      queryKey: ['park', id],
      queryFn: () => getPark({ id }),
    })),
  });

  const toggle = (id: number, name: string) => {
    setSelection((previous) => {
      if (previous.ids.includes(id)) {
        return {
          ids: previous.ids.filter((value) => value !== id),
          message: `${name}을 비교에서 제거했습니다.`,
        };
      }
      if (previous.ids.length >= 3) {
        return {
          ...previous,
          message: `${name}을 담을 수 없습니다. 최대 3개까지 비교할 수 있어요. 기존 공원을 먼저 제거해주세요.`,
        };
      }
      return {
        ids: [...previous.ids, id],
        message: `${name}을 비교에 담았습니다.`,
      };
    });
  };

  return (
    <ParkCompareContext.Provider value={{ ids: selection.ids, toggle }}>
      {children}
      <div
        role='status'
        aria-live='polite'
        aria-atomic='true'
        className='pointer-events-none fixed bottom-20 left-1/2 z-60 w-[calc(100%-2rem)] max-w-sm -translate-x-1/2'
      >
        {selection.message && (
          <p className='rounded-card border border-border bg-surface px-4 py-3 text-sm shadow-card'>
            {selection.message}
          </p>
        )}
      </div>
    </ParkCompareContext.Provider>
  );
};
