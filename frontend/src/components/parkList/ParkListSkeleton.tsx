import { ParkCardSkeleton } from './ParkCardSkeleton';

export const ParkListSkeleton = () => {
  return (
    <section className='mx-auto my-6 max-w-5xl space-y-6 px-6'>
      <header>
        <div className='h-9 w-40 animate-pulse rounded-md bg-border' />

        <div className='mt-3 h-5 w-48 animate-pulse rounded-md bg-border' />
      </header>

      {/* 필터 */}
      <div className='flex gap-3'>
        <div className='h-10 w-24 animate-pulse rounded-button bg-border' />
        <div className='h-10 w-24 animate-pulse rounded-button bg-border' />
      </div>

      {/* 카드 */}
      <div className='grid gap-5 md:grid-cols-2'>
        {Array.from({ length: 8 }).map((_, index) => (
          <ParkCardSkeleton key={index} />
        ))}
      </div>
    </section>
  );
};
