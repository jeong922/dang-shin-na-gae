import { LocateFixed } from 'lucide-react';

export const Map = () => {
  return (
    <section className='relative h-[calc(100dvh-8rem)] overflow-hidden rounded-2xl border border-border bg-slate-100 shadow-sm'>
      <div
        className='absolute inset-0 opacity-40'
        style={{
          backgroundImage: `
            linear-gradient(to right, rgba(148,163,184,.15) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(148,163,184,.15) 1px, transparent 1px)
          `,
          backgroundSize: '32px 32px',
        }}
      />

      <div className='absolute inset-0 flex flex-col items-center justify-center text-center'>
        <div className='rounded-2xl border border-border bg-white px-6 py-5 shadow-lg'>
          <p className='text-lg font-semibold text-text-primary'>지도 영역</p>
        </div>
      </div>

      <button className='absolute right-4 top-4 rounded-xl border border-border bg-white p-3 shadow transition hover:bg-slate-50'>
        <LocateFixed size={20} />
      </button>
    </section>
  );
};
