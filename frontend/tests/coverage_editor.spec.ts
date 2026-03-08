import { test, expect } from '@playwright/test';

test.describe('Coverage Polygon Editor QA', () => {
  let jsErrors: string[] = [];

  test.beforeEach(async ({ page }) => {
    jsErrors = [];
    page.on('pageerror', (err) => {
      jsErrors.push(err.message);
    });
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        jsErrors.push(msg.text());
      }
    });
    
    // Mock the coverage API endpoint since this is a UI-focused test
    await page.route('*/api/v1/agency/*/coverage/', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            type: "Feature",
            geometry: {
              type: "Polygon",
              coordinates: [[[30.0, 31.0], [30.1, 31.0], [30.1, 31.1], [30.0, 31.1], [30.0, 31.0]]]
            },
            properties: { area_km2: 10.5, vertex_count: 5 }
          })
        });
      } else if (route.request().method() === 'PUT') {
        // Assert the payload shape
        const actualPayload = JSON.parse(route.request().postData() || '{}');
        expect(actualPayload.coverage_polygon).toBeDefined();
        expect(actualPayload.coverage_polygon.type).toBe('Polygon');
        expect(actualPayload.coverage_polygon.coordinates).toBeDefined();
        
        // Assert GeoJSON validity (first must equal last coordinate)
        const coords = actualPayload.coverage_polygon.coordinates[0];
        const first = coords[0];
        const last = coords[coords.length - 1];
        expect(first[0]).toBeCloseTo(last[0]);
        expect(first[1]).toBeCloseTo(last[1]);

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Coverage area updated successfully.' })
        });
      }
    });
  });

  test('editor loads existing geometry and saves successfully with 0 JS errors', async ({ page }) => {
    // Navigate to the editor page (assuming local auth or mocked routing)
    // We navigate to a dummy agency ID
    await page.goto('/agency/dashboard/coverage');
    
    // Wait for map container to be visible
    const mapContainer = page.locator('.leaflet-container');
    await expect(mapContainer).toBeVisible({ timeout: 10000 });

    // Assert the polygon render (e.g. SVG path rendered by Leaflet)
    const polygonPath = page.locator('.leaflet-overlay-pane path');
    await expect(polygonPath).toBeVisible();

    // Emulate clicking save
    const saveButton = page.getByRole('button', { name: /save/i });
    await expect(saveButton).toBeVisible();
    await saveButton.click();

    // Verify successful toast message
    const successToast = page.getByText(/Coverage area updated successfully/i);
    await expect(successToast).toBeVisible();

    // Final Zero Defect Rule: Verify no JS errors
    expect(jsErrors.length).toBe(0);
  });
});
