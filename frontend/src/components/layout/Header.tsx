import { PawPrint } from 'lucide-react';
import { Link } from 'react-router';

export const Header = () => {
  return (
    <header className='sticky top-0 z-50 border-b border-border/60 bg-surface'>
      <div className='mx-auto flex h-16 max-w-7xl items-center px-4 sm:px-6 lg:px-8'>
        <Link to='/' aria-label='댕 신나개 홈' className='group flex items-center gap-2.5'>
          <PawPrint
            size={25}
            strokeWidth={2.2}
            className='text-[#6B7280] '
          />

          <span className='text-heading font-semibold tracking-tight tracking-[-0.03em] text-text-primary'>댕 신나개</span>
        </Link>
      </div>
    </header>
  );
};
