export const formatPercent = (value: number) => {
  return new Intl.NumberFormat('ko-KR', {
    style: 'percent',
    maximumFractionDigits: 1,
  }).format(value);
};

export const formatMeter = (value: number) => {
  return new Intl.NumberFormat('ko-KR', {
    maximumFractionDigits: 0,
  }).format(value);
};

export const formatArea = (value: number) => {
  const formatter = new Intl.NumberFormat('ko-KR', {
    maximumFractionDigits: 2,
  });

  if (value >= 1_000_000) {
    return `${formatter.format(value / 1_000_000)}㎢`;
  }

  return `${formatter.format(value)}㎡`;
};
