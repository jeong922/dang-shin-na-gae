import { NavLink } from 'react-router';
import { Map, List } from 'lucide-react';

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
];

export const Navbar = () => {
  return (
    <nav className='sticky bottom-0 z-50 border-t border-border bg-surface/80 backdrop-blur-md'>
      <div className='mx-auto flex h-16 max-w-5xl items-center justify-around px-4'>
        {menus.map(({ label, icon: Icon, path }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            className={({ isActive }) =>
              `group flex flex-col items-center gap-1 transition-colors ${
                isActive ? 'text-brand' : 'text-text-muted hover:text-brand'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  size={22}
                  strokeWidth={isActive ? 2.5 : 2}
                  className={`transition-transform duration-200 ${isActive ? 'scale-110' : 'group-hover:scale-110'}`}
                />

                <span className='text-caption font-medium'>{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
};
