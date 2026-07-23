import { Link } from 'react-router';
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
          <Link
            key={path}
            to={path}
            className='group flex flex-col items-center gap-1 text-text-muted transition-colors hover:text-brand'
          >
            <Icon size={22} className='transition-transform duration-200 group-hover:scale-110' />

            <span className='text-caption font-medium'>{label}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
};
