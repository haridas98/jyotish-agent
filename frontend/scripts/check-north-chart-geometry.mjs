import {
  chartTextStackBounds,
  northIndianHouseCells,
  northIndianHousePolygons,
} from "../src/lib/northIndianChartGeometry.ts";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function pointInPolygon(point, polygon) {
  let inside = false;
  for (let index = 0, previous = polygon.length - 1; index < polygon.length; previous = index++) {
    const currentPoint = polygon[index];
    const previousPoint = polygon[previous];
    const intersects =
      currentPoint.y > point.y !== previousPoint.y > point.y &&
      point.x <
        ((previousPoint.x - currentPoint.x) * (point.y - currentPoint.y)) /
          (previousPoint.y - currentPoint.y) +
          currentPoint.x;
    if (intersects) inside = !inside;
  }
  return inside;
}

const houses = Object.keys(northIndianHousePolygons).map(Number).sort((a, b) => a - b);
assert(houses.length === 12, `Expected 12 north Indian chart houses, got ${houses.length}`);

for (const house of houses) {
  const polygon = northIndianHousePolygons[house];
  const cell = northIndianHouseCells[house];
  assert(cell, `Missing text cell for house ${house}`);
  assert(pointInPolygon({ x: cell.centerX, y: cell.centerY }, polygon), `House ${house} label center is outside its polygon`);

  for (const lineCount of [1, 3, 6, 9]) {
    const lineGap = lineCount > 5 ? 11 : 13;
    const bounds = chartTextStackBounds(cell.centerY, lineCount, lineGap);
    assert(bounds.firstY >= 18, `House ${house} text stack starts too high for ${lineCount} lines`);
    assert(bounds.lastY <= 382, `House ${house} text stack ends too low for ${lineCount} lines`);
  }
}

console.log(JSON.stringify({ status: "ok", houses: houses.length }));
