import { useEffect, useState } from 'react';
import { LoaderCircle, TriangleAlert } from 'lucide-react';
import { Button } from '../ui/Button';

export interface MapRequestState {
  isFetching: boolean;
  hasData: boolean;
  error: Error | null;
  refetch: () => unknown;
}

export const MapRequestStatus = ({ isFetching, hasData, error, refetch }: MapRequestState) => {
  const [isDelayed, setIsDelayed] = useState(false);

  useEffect(() => {
    if (!isFetching) return;
    const timer = setTimeout(() => setIsDelayed(true), 5_000);
    return () => clearTimeout(timer);
  }, [isFetching]);

  if (isFetching && !isDelayed) return null;
  if (!isFetching && !error) return null;

  return (
    <div
      role={isFetching ? 'status' : 'alert'}
      className='absolute bottom-6 left-1/2 z-10 w-[calc(100%-2rem)] max-w-sm -translate-x-1/2 rounded-2xl bg-white p-4 text-sm shadow-md'
    >
      {isFetching ? (
        <div className='flex items-start gap-3'>
          <LoaderCircle size={20} className='shrink-0 animate-spin text-brand' />
          <div>
            <p className='font-semibold'>{hasData ? '응답이 지연되고 있어요.' : '서버를 시작하는 데 시간이 걸릴 수 있어요.'}</p>
            <p className='mt-1 text-text-muted'>공원 정보를 불러오고 있습니다. 잠시만 기다려주세요.</p>
          </div>
        </div>
      ) : (
        <div>
          <p className='flex items-center gap-2 font-semibold'>
            <TriangleAlert size={20} className='shrink-0 text-red-500' />
            공원 정보를 불러올 수 없습니다.
          </p>
          <p className='mt-2 text-text-muted'>{error?.message}</p>
          <Button className='mt-3 px-4 text-sm' onClick={() => { refetch(); }}>다시 시도</Button>
        </div>
      )}
    </div>
  );
};
