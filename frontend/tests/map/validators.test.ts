import { validateCoveragePolygon, sanitizeGeoJSON } from '../../src/lib/map/validators';
import { Feature, Polygon } from 'geojson';

describe('GeoJSON Validators', () => {
  describe('validateCoveragePolygon', () => {
    it('rejects unclosed or too small polygons', () => {
      const feature: Feature<Polygon> = {
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: [
            [[0, 0], [1, 1], [0, 1]] // Missing closing [0, 0]
          ]
        },
        properties: {}
      };

      const result = validateCoveragePolygon(feature);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('Ring must be closed');
    });

    it('rejects self-intersecting polygons', () => {
      const feature: Feature<Polygon> = {
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: [
            // Hourglass shape (intersecting)
            [[0, 0], [1, 1], [0, 1], [1, 0], [0, 0]]
          ]
        },
        properties: {}
      };

      const result = validateCoveragePolygon(feature);
      expect(result.valid).toBe(false);
      expect(result.error).toContain('cannot self-intersect');
    });

    it('allows valid polygons', () => {
      const feature: Feature<Polygon> = {
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: [
            [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
          ]
        },
        properties: {}
      };

      const result = validateCoveragePolygon(feature);
      expect(result.valid).toBe(true);
      expect(result.error).toBeUndefined();
    });
  });

  describe('sanitizeGeoJSON', () => {
    it('removes script tags and truncates lengths', () => {
      const feature: Feature<Polygon> = {
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
        },
        properties: {
          name: '<script>alert("xss")</script>My Area',
          safeValue: 42,
          booleanProp: true,
          nestedObj: { invalid: 'should be stripped' }
        }
      };

      const sanitized = sanitizeGeoJSON(feature);
      expect(sanitized.properties?.name).toBe('alert("xss")My Area');
      expect(sanitized.properties?.safeValue).toBe(42);
      expect(sanitized.properties?.booleanProp).toBe(true);
      expect(sanitized.properties?.nestedObj).toBeUndefined();
    });
  });
});
