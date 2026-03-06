import { Feature, Polygon, MultiPolygon, Position } from 'geojson';
import DOMPurify from 'dompurify';

/**
 * Checks if two line segments (p1-p2 and p3-p4) intersect.
 * Uses orientation-based intersection logic.
 */
function doIntersect(
  p1: Position,
  p2: Position,
  p3: Position,
  p4: Position
): boolean {
  const orientation = (a: Position, b: Position, c: Position) => {
    const val = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1]);
    if (Math.abs(val) < 1e-10) return 0; // collinear
    return val > 0 ? 1 : 2; // clock or counterclock wise
  };

  const onSegment = (a: Position, b: Position, c: Position) => {
    return (
      b[0] <= Math.max(a[0], c[0]) &&
      b[0] >= Math.min(a[0], c[0]) &&
      b[1] <= Math.max(a[1], c[1]) &&
      b[1] >= Math.min(a[1], c[1])
    );
  };

  const o1 = orientation(p1, p2, p3);
  const o2 = orientation(p1, p2, p4);
  const o3 = orientation(p3, p4, p1);
  const o4 = orientation(p3, p4, p2);

  if (o1 !== o2 && o3 !== o4) return true;

  if (o1 === 0 && onSegment(p1, p3, p2)) return true;
  if (o2 === 0 && onSegment(p1, p4, p2)) return true;
  if (o3 === 0 && onSegment(p3, p1, p4)) return true;
  if (o4 === 0 && onSegment(p3, p2, p4)) return true;

  return false;
}

/**
 * Check if a polygon ring self-intersects
 */
function hasSelfIntersection(ring: Position[]): boolean {
  for (let i = 0; i < ring.length - 1; i++) {
    for (let j = i + 2; j < ring.length - 1; j++) {
      // Don't compare adjacent segments, or first/last segment at the ends (which share a vertex)
      if (i === 0 && j === ring.length - 2) continue;
      // Also ignore exactly adjacent segments where intersection is just the shared point
      if (j === i + 1) continue;
      
      const p1 = ring[i];
      const p2 = ring[i + 1];
      const p3 = ring[j];
      const p4 = ring[j + 1];
      
      if (doIntersect(p1, p2, p3, p4)) {
        return true;
      }
    }
  }
  return false;
}

export function validateCoveragePolygon(
  feature: Feature<Polygon | MultiPolygon> | null | undefined
): { valid: boolean; error?: string } {
  if (!feature || feature.type !== 'Feature') {
    return { valid: false, error: 'Invalid Feature object' };
  }

  const geom = feature.geometry;
  if (!geom || (geom.type !== 'Polygon' && geom.type !== 'MultiPolygon')) {
    return { valid: false, error: 'Geometry must be a Polygon or MultiPolygon' };
  }

  const checkRing = (ring: Position[]) => {
    if (ring.length < 4) {
      return 'Ring must have at least 4 coordinates (3 unique vertices plus closure)';
    }

    const first = ring[0];
    const last = ring[ring.length - 1];

    if (first[0] !== last[0] || first[1] !== last[1]) {
      return 'Ring must be closed (first and last coordinate must match)';
    }

    if (hasSelfIntersection(ring)) {
      return 'Polygon cannot self-intersect';
    }

    return null;
  };

  if (geom.type === 'Polygon') {
    for (const ring of geom.coordinates) {
      const err = checkRing(ring);
      if (err) return { valid: false, error: err };
    }
  } else {
    for (const polygon of geom.coordinates) {
      for (const ring of polygon) {
        const err = checkRing(ring);
        if (err) return { valid: false, error: err };
      }
    }
  }

  return { valid: true };
}

export function sanitizeGeoJSON<T extends Feature>(feature: T): T {
  if (!feature.properties) {
    return feature;
  }

  const sanitizedProps: Record<string, any> = {};
  for (const [key, value] of Object.entries(feature.properties)) {
    if (typeof value === 'string') {
      const safeStr = DOMPurify.sanitize(value, { ALLOWED_TAGS: [] }).substring(0, 100);
      sanitizedProps[key] = safeStr;
    } else if (typeof value === 'number' || typeof value === 'boolean') {
      sanitizedProps[key] = value;
    }
  }

  return {
    ...feature,
    properties: sanitizedProps,
  };
}
