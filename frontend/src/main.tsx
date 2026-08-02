import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import 'maplibre-gl/dist/maplibre-gl.css';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createBrowserRouter, RouterProvider } from 'react-router';
import { RootLayout } from './layouts/RootLayout.tsx';
import { HomePage } from './pages/HomePage.tsx';
import { ParksPage } from './pages/ParksPage.tsx';
import { ParkDetailPage } from './pages/ParkDetailPage.tsx';

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
      { index: true, Component: HomePage },
      { path: 'parks', Component: ParksPage },
      {
        path: 'parks/:parkId',
        Component: ParkDetailPage,
      },
    ],
  },
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>,
);
