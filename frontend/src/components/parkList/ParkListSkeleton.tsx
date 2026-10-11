import { ParkCardSkeleton } from '../park/ParkCardSkeleton';

export const ParkListSkeleton = () => {
  return (
    <>


      <div className='grid gap-5 md:grid-cols-2'>
        {Array.from({ length: 8 }).map((_, index) => (
          <ParkCardSkeleton key={index} />
        ))}
      </div>
    </>
  );
};
