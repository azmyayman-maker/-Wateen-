# =============================================================================
# Ticket 2.3 — Integration Trial Run (Automated)
# =============================================================================
$ErrorActionPreference = "Continue"
$COMPOSE_FILE = "D:\projects\Wateen\docker\docker-compose.yml"
$PROJECT_DIR  = "D:\projects\Wateen"
$DC = "docker compose -f $COMPOSE_FILE --project-directory $PROJECT_DIR"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " STEP 1: Tearing down old containers" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Invoke-Expression "$DC down --remove-orphans 2>&1"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " STEP 2: Rebuilding & starting services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Invoke-Expression "$DC up --build -d 2>&1"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " STEP 3: Waiting for health checks (30s)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Start-Sleep -Seconds 30

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " STEP 4: Running database migrations" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Invoke-Expression "$DC exec -T web python manage.py migrate --no-input 2>&1"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " STEP 5: Geo-Engine Smoke Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Invoke-Expression "$DC exec -T web python -c @'
import sys, time, logging
logging.basicConfig(level=logging.WARNING)
print('\n--- SMOKE TEST START ---')
try:
    from visits.services.matching import GeoMatchingService
    svc = GeoMatchingService()
    ok = svc.update_nurse_location(999, 30.0444, 31.2357)
    if not ok:
        print('FAIL: Could not write to Redis'); sys.exit(1)
    print('  [1/4] Nurse location stored')
    time.sleep(0.1)
    c = svc.find_candidates(30.0450, 31.2360, radius_km=5)
    if not any(x['nurse_id']==999 for x in c):
        print('FAIL: Nurse not found in radius'); sys.exit(1)
    print('  [2/4] Candidate search OK:', c)
    loc = svc.get_nurse_location(999)
    if loc is None:
        print('FAIL: GEOPOS returned None'); sys.exit(1)
    print(f'  [3/4] GEOPOS OK: lat={loc[0]:.4f} lng={loc[1]:.4f}')
    svc.remove_nurse(999)
    print('  [4/4] Cleanup OK')
    print('\nSUCCESS: Redis is reachable and Geo-Engine is active')
except Exception as e:
    print(f'CRITICAL ERROR: {e}'); sys.exit(1)
finally:
    print('--- SMOKE TEST END ---\n')
'@ 2>&1"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " STEP 6: Container status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Invoke-Expression "$DC ps 2>&1"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host " INTEGRATION TRIAL COMPLETE" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green
