import './index.css';
import { StrictMode, Suspense } from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createBrowserRouter, RouterProvider } from 'react-router';
import { RootLayout } from './layouts/RootLayout.tsx';
import { LoadingOverlay } from './components/ui/loading/LoadingOverlay.tsx';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      gcTime: 1000 * 60 * 10,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const router = createBrowserRouter([
  {
    path: '/',
    Component: RootLayout,
    children: [
      {
        index: true,
        lazy: async () => {
          const { default: HomePage } = await import('./pages/HomePage');
          return {
            Component: HomePage,
          };
        },
      },
      {
        path: 'parks',
        lazy: async () => {
          const { default: ParksPage } = await import('./pages/ParksPage');
          return {
            Component: ParksPage,
          };
        },
      },
      {
        path: 'parks/:parkId',
        lazy: async () => {
          const { default: ParkDetailPage } = await import('./pages/ParkDetailPage');
          return {
            Component: ParkDetailPage,
          };
        },
      },
    ],
  },
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <Suspense fallback={<LoadingOverlay title='페이지를 불러오는 중' description='잠시만 기다려주세요.' />}>
        <RouterProvider router={router} />
      </Suspense>
    </QueryClientProvider>
  </StrictMode>,
);
