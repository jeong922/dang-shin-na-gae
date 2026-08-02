import { ImageOff } from 'lucide-react';
import { useState } from 'react';

interface Props {
  src?: string;
  alt: string;
  fallbackText?: string;
  className?: string;
}

export const ImageWithFallback = ({ src, alt, className, fallbackText = '이미지를 불러올 수 없습니다.' }: Props) => {
  const [isError, setIsError] = useState(false);

  if (!src || isError) {
    return (
      <div className={`flex items-center justify-center bg-slate-100 text-text-muted ${className}`}>
        <div className='flex flex-col items-center gap-2'>
          <ImageOff size={32} />
          <span className='text-sm'>{fallbackText}</span>
        </div>
      </div>
    );
  }

  return <img src={src} alt={alt} loading='lazy' className={className} onError={() => setIsError(true)} />;
};
