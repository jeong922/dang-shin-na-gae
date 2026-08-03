import { ParkCardSkeleton } from './ParkCardSkeleton';

export const ParkListSkeleton = () => {
  return (
    <>
      <header>
        <div className='h-9 w-40 animate-pulse rounded-md bg-border' />
        <div className='mt-3 h-5 w-48 animate-pulse rounded-md bg-border' />
      </header>

      <div className='grid gap-5 md:grid-cols-2'>
        {Array.from({ length: 8 }).map((_, index) => (
          <ParkCardSkeleton key={index} />
        ))}
      </div>
    </>
  );
};
