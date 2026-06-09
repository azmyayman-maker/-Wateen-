import { test, expect } from '@playwright/test';

test('Dashboard degrades elegantly to HTTP polling upon WebSocket failure', async ({ page }) => {
  // Forcefully sever the WebSocket connection using Playwright Route Interception 
  await page.route('**/ws/dashboard/agency/', route => route.abort('connectionreset'));
  
  // Intercept the HTTP fallback
  await page.route('**/api/v1/dashboard/metrics/', async route => {
    const json = {
      metrics: {
        active_visits: 99,
        queue_depth: 0,
        online_nurses: 10,
        revenue: { escrowed: "100.00", settled: "50.00" }
      }
    };
    await route.fulfill({ json });
  });

  await page.goto('/agency/dashboard');

  // Verify the pulse state triggers initially while parsing WS breakdown
  await expect(page.locator('text=جاري تحميل لوحة التحكم...')).toBeVisible();

  // Wait for 30s timeout or fast-forward time to assert HTTP fallback injection
  // Mocks ensure the HTTP fallback text replaces the empty pulse seamlessly
  await expect(page.locator('text=99')).toBeVisible({ timeout: 35000 });
});
