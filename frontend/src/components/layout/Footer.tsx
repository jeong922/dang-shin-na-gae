export const Footer = () => {
  return (
    <footer className='border-t border-border bg-surface'>
      <div className='mx-auto max-w-7xl px-4 py-6 text-center'>
        <p className='text-sm font-medium text-text-secondary'>© 2026 댕 신나개</p>

        <div className='mt-3 space-y-1 text-caption text-text-muted'>
          <p>공원 정보: 서울시 주요 공원현황 · 서울열린데이터광장</p>
          <p>공간 정보: 서울시 생활권계획 시설(공원) 공간정보 · 서울열린데이터광장</p>
          <p>서울특별시 제공 · 공공누리 제1유형</p>
          <p>공공데이터를 전처리·가공하여 서비스에 활용했습니다.</p>
        </div>
      </div>
    </footer>
  );
};
