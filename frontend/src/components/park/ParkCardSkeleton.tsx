export const ParkCardSkeleton = () => {
  return (
    <article className='rounded-card bg-surface p-5 shadow-card'>
      {/* 제목 */}
      <div className='h-6 w-2/3 animate-pulse rounded-md bg-border' />

      {/* 지역 */}
      <div className='mt-3 h-4 w-1/3 animate-pulse rounded-md bg-border' />

      {/* 정보 영역 */}
      <div className='mt-5 grid grid-cols-2 gap-4'>
        <div className='space-y-2'>
          <div className='h-3 w-16 animate-pulse rounded bg-border' />
          <div className='h-5 w-20 animate-pulse rounded bg-border' />
        </div>

        <div className='space-y-2'>
          <div className='h-3 w-16 animate-pulse rounded bg-border' />
          <div className='h-5 w-20 animate-pulse rounded bg-border' />
        </div>
      </div>

      {/* 난이도 */}
      <div className='mt-5 flex items-center justify-between'>
        <div className='h-3 w-16 animate-pulse rounded bg-border' />

        <div className='h-6 w-16 animate-pulse rounded-full bg-border' />
      </div>
    </article>
  );
};
