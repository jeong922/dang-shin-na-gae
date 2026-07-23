import { Link } from 'react-router';
import { PawPrint } from 'lucide-react';

export const Header = () => {
  return (
    <header className='sticky top-0 z-50 border-b border-border bg-white/80 shadow-header backdrop-blur-md'>
      <div className='mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8'>
        <Link
          to='/'
          aria-label='댕신나개 홈'
          className='group flex items-center gap-3 transition-transform active:scale-95'
        >
          <div className='flex h-10 w-10 items-center justify-center rounded-logo bg-brand text-white shadow-md shadow-brand/20 transition-all group-hover:bg-brand-hover group-hover:shadow-lg group-hover:shadow-brand/30'>
            <PawPrint size={22} className='transition-transform duration-200 group-hover:scale-110' />
          </div>

          <div className='flex flex-col'>
            <span className='text-lg font-black tracking-tight text-text-primary'>댕 신나개</span>
          </div>
        </Link>
      </div>
    </header>
  );
};
