import { Outlet } from 'react-router';

import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { Navbar } from '../components/Navbar';

export const RootLayout = () => {
  return (
    <div className='flex min-h-dvh max-w-5xl mx-auto flex-col bg-background'>
      <Header />

      <main className='flex-1'>
        <Outlet />
      </main>
      <Footer />

      <Navbar />
    </div>
  );
};
