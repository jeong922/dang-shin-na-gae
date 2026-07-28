import { parks } from '../mocks/parks';
import { ParkCard } from '../components/ParkCard';

export const Parks = () => {
  return (
    <section className='mx-auto max-w-5xl space-y-6 my-6 px-6'>
      <header>
        <h1 className='text-3xl font-bold'>공원 목록</h1>
        <p className='mt-1 text-text-muted'>
          총 <span className='font-semibold text-brand'>{parks.length}</span>개의 공원
        </p>
      </header>

      {/* 필터 구현 필요 */}
      <div className='flex gap-3'>
        <button className='rounded-full border border-border bg-white px-4 py-2 text-sm font-medium hover:bg-gray-50'>
          난이도
        </button>

        <button className='rounded-full border border-border bg-white px-4 py-2 text-sm font-medium hover:bg-gray-50'>
          지역
        </button>
      </div>

      <div className='grid gap-5 md:grid-cols-2'>
        {parks.map((park) => (
          <ParkCard park={park} />
        ))}
      </div>
    </section>
  );
};
