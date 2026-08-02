export const Footer = () => {
  return (
    <footer className='border-t border-border bg-surface'>
      <div className='mx-auto max-w-7xl px-4 py-6 text-center text-caption text-text-muted'>
        <p className='font-medium text-text-secondary'>© 2026 댕 신나개</p>

        <div className='mt-3 space-y-1'>
          <p>공원 데이터 출처: 서울 열린데이터 광장</p>

          <p>서울특별시 제공 · 공공누리 제1유형(출처표시)</p>

          <p>본 서비스는 공공데이터를 전처리 및 가공하여 활용하였습니다.</p>
        </div>
      </div>
    </footer>
  );
};
