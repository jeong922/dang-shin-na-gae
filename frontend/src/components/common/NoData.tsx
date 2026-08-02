export const NoData = ({ message = '제공되는 정보가 없습니다.' }: { message?: string }) => (
  <p className='text-sm text-text-muted'>{message}</p>
);
