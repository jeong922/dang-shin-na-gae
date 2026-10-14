import { NavLink } from 'react-router';
import { Map, List, Columns3 } from 'lucide-react';
import { useParkCompare } from '../../hooks/useParkCompare';

const menus = [
  {
    label: '지도',
    icon: Map,
    path: '/',
  },
  {
    label: '공원 목록',
    icon: List,
    path: '/parks',
  },
  {
    label: '공원 비교',
    icon: Columns3,
    path: '/compare',
  },
];

export const Navbar = () => {
  const { ids } = useParkCompare();
  return (
    <nav className='sticky bottom-0 z-50 border-t border-border bg-surface'>
      <div className='mx-auto flex h-16 max-w-5xl items-center justify-around px-4'>
        {menus.map(({ label, icon: Icon, path }) => (
          <NavLink
            key={path}
            to={path}
            aria-label={
              path === '/compare'
                ? `공원 비교 ${ids.length}개 선택됨, 최대 3개`
                : undefined
            }
            end={path === '/'}
            className={({ isActive }) =>
              `group flex flex-col items-center gap-1 transition-colors ${
                isActive ? 'text-brand' : 'text-text-muted hover:text-brand'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={22} strokeWidth={isActive ? 2.5 : 2} />

                <span className='text-caption font-medium'>
                  {label}
                  {path === '/compare' && ` ${ids.length}/3`}
                </span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
};
