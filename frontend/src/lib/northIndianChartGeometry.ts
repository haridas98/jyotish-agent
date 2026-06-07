export type ChartPoint = { x: number; y: number };

export const northIndianHousePolygons: Record<number, ChartPoint[]> = {
  1: [
    { x: 200, y: 2 },
    { x: 300, y: 100 },
    { x: 200, y: 200 },
    { x: 100, y: 100 },
  ],
  2: [
    { x: 2, y: 2 },
    { x: 200, y: 2 },
    { x: 100, y: 100 },
  ],
  3: [
    { x: 2, y: 2 },
    { x: 100, y: 100 },
    { x: 2, y: 200 },
  ],
  4: [
    { x: 2, y: 200 },
    { x: 100, y: 100 },
    { x: 200, y: 200 },
    { x: 100, y: 300 },
  ],
  5: [
    { x: 2, y: 200 },
    { x: 100, y: 300 },
    { x: 2, y: 398 },
  ],
  6: [
    { x: 2, y: 398 },
    { x: 100, y: 300 },
    { x: 200, y: 398 },
  ],
  7: [
    { x: 200, y: 398 },
    { x: 100, y: 300 },
    { x: 200, y: 200 },
    { x: 300, y: 300 },
  ],
  8: [
    { x: 200, y: 398 },
    { x: 300, y: 300 },
    { x: 398, y: 398 },
  ],
  9: [
    { x: 398, y: 398 },
    { x: 300, y: 300 },
    { x: 398, y: 200 },
  ],
  10: [
    { x: 398, y: 200 },
    { x: 300, y: 100 },
    { x: 200, y: 200 },
    { x: 300, y: 300 },
  ],
  11: [
    { x: 398, y: 2 },
    { x: 398, y: 200 },
    { x: 300, y: 100 },
  ],
  12: [
    { x: 200, y: 2 },
    { x: 398, y: 2 },
    { x: 300, y: 100 },
  ],
};

export const northIndianHouseCells = Object.fromEntries(
  Object.entries(northIndianHousePolygons).map(([house, polygon]) => {
    const center = polygonCentroid(polygon);
    return [Number(house), { centerX: center.x, centerY: center.y }];
  }),
) as Record<number, { centerX: number; centerY: number }>;

export function polygonCentroid(points: ChartPoint[]) {
  let doubledArea = 0;
  let x = 0;
  let y = 0;
  points.forEach((point, index) => {
    const next = points[(index + 1) % points.length];
    const cross = point.x * next.y - next.x * point.y;
    doubledArea += cross;
    x += (point.x + next.x) * cross;
    y += (point.y + next.y) * cross;
  });
  if (doubledArea === 0) {
    return {
      x: points.reduce((sum, point) => sum + point.x, 0) / points.length,
      y: points.reduce((sum, point) => sum + point.y, 0) / points.length,
    };
  }
  return { x: x / (3 * doubledArea), y: y / (3 * doubledArea) };
}

export function firstSymbolLineY(centerY: number, lineCount: number, lineGap: number) {
  return centerY - ((lineCount - 1) * lineGap) / 2;
}

export function safeSymbolCenterY(centerY: number, lineCount: number, lineGap: number) {
  const halfHeight = ((lineCount - 1) * lineGap) / 2;
  const min = 18 + halfHeight;
  const max = 382 - halfHeight;
  if (min > max) return 200;
  return Math.min(Math.max(centerY, min), max);
}

export function chartTextStackBounds(centerY: number, lineCount: number, lineGap: number) {
  const firstY = firstSymbolLineY(safeSymbolCenterY(centerY, lineCount, lineGap), lineCount, lineGap);
  return {
    firstY,
    lastY: firstY + (lineCount - 1) * lineGap,
  };
}
