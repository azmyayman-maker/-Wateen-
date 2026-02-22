from playwright.sync_api import sync_playwright
import time
import os

ARTIFACTS_DIR = 'C:/Users/AdminOS/.gemini/antigravity/brain/3e15d3ab-58b6-427a-b4c9-54d232f740cf'
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 900})
    page.goto('http://localhost:3000/register', timeout=30000)
    page.wait_for_load_state('networkidle')
    time.sleep(3)
    
    # Step 1: Screenshot initial state
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, 'step1_overview.png'))
    print("Step 1 screenshot taken")
    
    # Click next button
    next_btn = page.locator('button:has-text("التالي")')
    next_btn.click()
    time.sleep(1.5)
    
    # Step 2: Screenshot password page
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, 'step2_empty.png'))
    print("Step 2 empty screenshot taken")
    
    # Type weak password
    pw_input = page.locator('input[type="password"]').first
    pw_input.fill('abc')
    time.sleep(0.5)
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, 'step2_weak_pw.png'))
    print("Weak password screenshot taken")
    
    # Type strong password
    pw_input.fill('')
    pw_input.fill('Test@1234')
    time.sleep(0.5)
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, 'step2_strong_pw.png'))
    print("Strong password screenshot taken")
    
    # Confirm password
    confirm_input = page.locator('input[placeholder="أعد إدخال كلمة المرور"]')
    confirm_input.fill('Test@1234')
    time.sleep(0.5)
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, 'step2_matched.png'))
    print("Matching passwords screenshot taken")
    
    # Click back button
    back_btn = page.locator('button:has-text("رجوع")')
    back_btn.click()
    time.sleep(1)
    page.screenshot(path=os.path.join(ARTIFACTS_DIR, 'step1_returned.png'))
    print("Returned to step 1 screenshot taken")
    
    print("All tests passed!")
    browser.close()
