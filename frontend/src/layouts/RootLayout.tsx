import { Outlet } from 'react-router';

import { Header } from '../components/layout/Header';
import { Footer } from '../components/layout/Footer';
import { Navbar } from '../components/layout/Navbar';
import { ParkCompareProvider } from '../contexts/ParkCompareContext';

export const RootLayout = () => {
  return (
    <ParkCompareProvider>
      <div className='flex min-h-dvh max-w-5xl mx-auto flex-col bg-background'>
        <Header />

        <main className='flex-1'>
          <Outlet />
        </main>
        <Footer />

        <Navbar />
      </div>
    </ParkCompareProvider>
  );
};
