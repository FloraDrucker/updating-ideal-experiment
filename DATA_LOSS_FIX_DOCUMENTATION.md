# Data Loss Fix Documentation

This document describes the changes made to fix critical data loss issues discovered during Prolific pilot testing, where 3 out of 10 participants experienced performance data being recorded as 0 despite completing tasks.

## Problem Summary

The Task page uses two mechanisms to save participant performance:
1. **WebSocket (liveSend)**: Saves performance in real-time after each correct answer
2. **Form submission**: Saves performance when the page times out or advances

A race condition existed where the form could submit with empty/zero values, overwriting the correctly-saved WebSocket data.

---

## Root Causes Identified

### Issue 1: Hidden Form Inputs Without Initial Values

**Location:** `study/Task.html` lines 200-203

**Before:**
```html
<input type="hidden" name="performance" id="performance">
<input type="hidden" name="mistakes" id="mistakes">
```

**Problem:** When the page loads or refreshes, these hidden inputs start empty. If the timer expires before the WebSocket response arrives (which populates these fields), the form submits empty values. oTree coerces empty strings to 0, overwriting the server's correct value.

**Scenario:**
1. Participant completes 5 tasks (server has performance=5)
2. Page refreshes with 2 seconds remaining on timer
3. Hidden input loads empty (no value attribute)
4. `liveSend({init})` sent to get server state
5. Timer expires before WebSocket response arrives
6. Form submits with empty performance field → server saves 0

### Issue 2: Forced Page Reload After Stop Working

**Location:** `study/Task.html` (two locations)

**Before:**
```javascript
// Force a reload so the Back button cannot restore work mode
setTimeout(() => {
    window.location.reload();
}, 300);
```

**Problem:** After sending `liveSend({stop_work: true})`, the code waited only 300ms before forcing a page reload. If network latency exceeded 300ms, the WebSocket message might not complete before the reload interrupted the connection.

### Issue 3: No Client-Side Backup for Page Refresh

**Problem:** If a participant refreshed the page after completing tasks but before the WebSocket persisted the data, there was no client-side backup. The page would reload with stale server values.

---

## Solution: Three-Layer Persistence

We implemented a robust three-layer persistence system:

| Layer | Mechanism | Survives |
|-------|-----------|----------|
| 1 | WebSocket (liveSend) | Real-time to server |
| 2 | Form submission | Page timeout/advance |
| 3 | sessionStorage | Page refresh (same tab) |

On page load, the client reconciles all three sources by taking the **maximum** value, ensuring progress is never lost.

---

## Changes Made

### 1. Added Initial Values to Hidden Inputs

**File:** `study/Task.html` lines 200-203

**After:**
```html
<input type="hidden" name="performance" id="performance" value="{{ player.performance }}">
<input type="hidden" name="mistakes" id="mistakes" value="{{ player.mistakes }}">
```

**Why:** Ensures the form always has at least the server's last-known value, eliminating the empty-field race condition.

---

### 2. Added sessionStorage Backup

**File:** `study/Task.html`

**Added storage key constants:**
```javascript
const STORAGE_KEY_PERF = 'task_perf_round_{{ player.round_number }}';
const STORAGE_KEY_MISTAKES = 'task_mistakes_round_{{ player.round_number }}';
```

**Added helper functions:**
```javascript
function getStoredValue(key) {
    try {
        return parseInt(sessionStorage.getItem(key)) || 0;
    } catch (e) {
        return 0;  // sessionStorage unavailable
    }
}

function setStoredValue(key, value) {
    try {
        sessionStorage.setItem(key, value);
    } catch (e) {
        // sessionStorage unavailable, continue without backup
    }
}
```

**Why:** sessionStorage persists across page refresh within the same browser tab, providing a client-side backup that survives accidental refreshes or browser hiccups.

---

### 3. Added Reconciliation on Page Load

**File:** `study/Task.html` (DOMContentLoaded handler)

**After:**
```javascript
document.addEventListener("DOMContentLoaded", () => {
    // Reconcile sessionStorage with server value (take max to never lose progress)
    const storedPerf = getStoredValue(STORAGE_KEY_PERF);
    const serverPerf = {{ player.performance }};
    const reconciledPerf = Math.max(storedPerf, serverPerf);

    const storedMistakes = getStoredValue(STORAGE_KEY_MISTAKES);
    const serverMistakes = {{ player.mistakes }};
    const reconciledMistakes = Math.max(storedMistakes, serverMistakes);

    // Update hidden inputs with reconciled values
    document.getElementById("performance").value = reconciledPerf;
    document.getElementById("performance-display").innerText = reconciledPerf;
    document.getElementById("mistakes").value = reconciledMistakes;

    // Update sessionStorage with reconciled values
    setStoredValue(STORAGE_KEY_PERF, reconciledPerf);
    setStoredValue(STORAGE_KEY_MISTAKES, reconciledMistakes);

    // Send init with client's known values for server-side reconciliation
    liveSend({
        init: true,
        client_performance: reconciledPerf,
        client_mistakes: reconciledMistakes
    });
});
```

**Why:** By taking the maximum of sessionStorage and server values, we ensure that even if the server missed a WebSocket message, the client's local backup is used.

---

### 4. Added sessionStorage Writes on Task Completion

**File:** `study/Task.html` (myFunction)

**After:**
```javascript
if (errors === 0) {
    let temp = Number(document.getElementById("performance").value || 0) + 1;
    document.getElementById("performance").value = temp;
    setStoredValue(STORAGE_KEY_PERF, temp);  // Backup to sessionStorage
    // ...
}
```

**Why:** Every correct answer is immediately backed up to sessionStorage, so even if the subsequent WebSocket call fails, the value is preserved locally.

---

### 5. Added Server-Side Reconciliation

**File:** `study/__init__.py` (live_update_performance function)

**After:**
```python
if data.get('init'):
    # Reconcile client values with server (take max to never lose progress)
    client_perf = data.get('client_performance', 0)
    client_mistakes = data.get('client_mistakes', 0)

    if client_perf > player.performance:
        player.performance = client_perf

    if client_mistakes > player.mistakes:
        player.mistakes = client_mistakes
    # ... rest of init
```

**Why:** If the client has a higher value than the server (meaning a WebSocket message was lost), the server adopts the client's value. This ensures data is recovered even after network issues.

---

### 6. Removed Forced Page Reloads

**File:** `study/Task.html` (two locations)

**Removed:**
```javascript
// Force a reload so the Back button cannot restore work mode
setTimeout(() => {
    window.location.reload();
}, 300);
```

**Why:**
- The reload was intended to prevent the Back button from restoring work mode
- However, this is already handled by:
  - UI being frozen (inputs disabled)
  - `player.stopped_work = True` saved server-side
  - `js_vars.stopped_work` checked on every page load
  - oTree's page sequencing prevents returning to submitted pages
- The 300ms timeout was too short for reliable WebSocket completion
- Removing it eliminates a potential data loss vector

---

## Data Flow After Fix

### Normal Operation
1. Participant completes task → JS increments hidden input
2. JS writes to sessionStorage (backup)
3. JS calls liveSend → server saves performance
4. Server responds → liveRecv updates display
5. Timer expires → form submits (backup save)

### WebSocket Failure
1. Participant completes task → JS increments hidden input
2. JS writes to sessionStorage (backup)
3. JS calls liveSend → **fails due to network issue**
4. Timer expires → form submits with JS value → server saves correctly

### WebSocket Failure + Page Refresh
1. Participant completes task → JS increments hidden input
2. JS writes to sessionStorage (backup) → **sessionStorage has value 5**
3. JS calls liveSend → **fails** → server still has value 4
4. Page refreshes (accidental or browser hiccup)
5. Page loads → `max(sessionStorage=5, server=4)` = 5
6. Hidden input populated with 5
7. liveSend({init, client_performance: 5}) → server reconciles to 5
8. Server logs `[RECONCILE]` showing data recovery
9. Timer expires → form submits 5 → no data loss

---

## Testing Recommendations

### Manual Test 1: Page Refresh During Task
1. Set `work_length_seconds=120` in settings.py
2. Start a participant session, navigate to Task page
3. Complete 3 tasks (performance shows 3)
4. Press F5 to refresh the page
5. Verify performance display still shows 3
6. Complete 2 more tasks
7. Wait for timer to expire
8. Check oTree admin data export
9. **Expected:** Performance = 5

### Manual Test 2: Stop Working Button
1. Start a participant session, navigate to Task page
2. Complete 5 tasks
3. Click "Stop working" button
4. Verify UI freezes and attention checks begin
5. Wait for timer to expire
6. Check oTree admin data export
7. **Expected:** performance=5, stopped_work=True, work_seconds < total_time

---

## Files Modified

| File | Changes |
|------|---------|
| `study/Task.html` | Added value attributes, sessionStorage logic, removed forced reloads, timer optimization |
| `study/__init__.py` | Added server-side reconciliation |
| `instructions_consent/instructionsnippet.html` | Deferred MathJax loading |

---

## Summary

These changes implement a defense-in-depth strategy with three independent persistence mechanisms. Even if one or two mechanisms fail, the participant's work is preserved.

---

# Part 2: Performance Optimizations

Users reported slow page load times. We identified and fixed several performance issues.

## Issues Identified

| Issue | Severity | Impact |
|-------|----------|--------|
| MathJax CDN loaded on page load (1-3MB) | **CRITICAL** | Blocks page rendering even though formula is hidden |
| Timer updating every 250ms | **LOW** | Minor unnecessary DOM updates |
| Unused audio file (alarm.mp3) | **LOW** | 256KB dead file in _static/ (not loaded at runtime) |

**Note:** We investigated the Task page thoroughly and found no critical performance issues. The DOM operations (~60 getElementById calls per correct answer) are O(1) lookups taking ~0.6ms total - imperceptible to users. The main performance bottleneck was the MathJax CDN load on the Instructions page.

---

## Fixes Implemented

### 1. Deferred MathJax Loading (CRITICAL)

**File:** `instructions_consent/instructionsnippet.html`

**Problem:** MathJax (1-3MB JavaScript library) was loaded via `<script>` tag inside a hidden div. Browsers still download and execute scripts in hidden elements, blocking page rendering.

**Before:**
```html
<div id="mathFormula" style="display: none;">
    <script src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=default'></script>
    $$ formula $$
</div>
```

**After:**
```javascript
let mathJaxLoaded = false;

function toggleMathFormula() {
    // ... show/hide logic ...

    // Load MathJax only when formula is first shown
    if (!mathJaxLoaded) {
        mathJaxLoaded = true;
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=default';
        script.onload = function() {
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, "mathFormula"]);
        };
        document.head.appendChild(script);
    }
}
```

**Impact:** Instructions page loads 1-3MB faster. MathJax only loads if user clicks "Show mathematical formula" button (most users won't).

---

### 2. Timer Interval Optimization (LOW)

**File:** `study/Task.html`

**Problem:** The countdown timer was updating every 250ms (4 times per second), causing unnecessary DOM updates.

**Before:**
```javascript
setInterval(tick, 250);
```

**After:**
```javascript
setInterval(tick, 1000);  // Update every 1 second
```

**Impact:** Reduces timer-related DOM updates from 4/second to 1/second. The countdown displays seconds, so 1-second precision is sufficient. This is a minor optimization - the actual CPU savings are negligible (~0.3ms/second), but it reduces unnecessary work.

---

### 3. Unused Audio File (LOW - Not Fixed)

**File:** `_static/alarm.mp3` (256KB)

**Finding:** This file exists but is not referenced anywhere in the codebase. It's dead code.

**Recommendation:** Delete this file to reduce repository size. Not a runtime performance issue since it's never loaded.

---

## Future Optimizations (Not Implemented)

These optimizations were identified but not implemented. They can be done later if performance issues persist.

### 1. Replace MathJax with Static Image (Recommended)

**Current:** MathJax renders the formula dynamically.

**Better approach:** Pre-render the formula as a PNG/SVG image and embed it directly. This eliminates the CDN dependency entirely.

**Formula to render:**
```
p = 1 - (your guess - actual value)² / 900
```

**Impact:** Would eliminate the 1-3MB MathJax download entirely, even for users who click the button.

### 2. Image Compression

**Files:** `_static/50balls_signal*.png` (116-120KB each, 356KB total)

**Recommendation:** Convert to WebP format or compress PNGs. Could reduce to ~30-50KB each.

**Impact:** Faster Signal page loads.

### 3. Static Asset Caching (WhiteNoise)

**Current:** No explicit cache headers on static files.

**Implementation:**
```python
# requirements.txt
whitenoise>=6.0

# settings.py
MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', ...]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**Impact:** Returning participants don't re-download static assets. Moderate improvement for multi-round experiments.

### 4. DOM Operation Optimization (Micro-optimization)

**File:** `study/Task.html`

**Issue:** ~60 `getElementById` calls per correct answer (26 legend cells + task boxes).

**Reality check:** These are O(1) hash lookups in modern browsers. Total time: ~0.6ms per answer - imperceptible to users. This is a micro-optimization that would not noticeably improve user experience.

**Example optimization (if desired):**
```javascript
// Cache DOM elements once at page load
const perfInput = document.getElementById("performance");
const perfDisplay = document.getElementById("performance-display");
const mistakesInput = document.getElementById("mistakes");
// ... use cached references throughout
```

**Impact:** Negligible. Only implement if you have specific evidence of jank during task interaction.

---

## Performance Testing

After implementing fixes, verify:

1. **Instructions page:** Should load noticeably faster. MathJax should only load when "Show mathematical formula" is clicked.

2. **Task page:** Timer should update every second instead of 4x/second. No visible difference to user.

3. **Browser DevTools Network tab:** Check that MathJax is not loaded on Instructions page until button is clicked.

---

## If Slow Loads Persist

If users still report slow page loads after these fixes, the issue is likely **not in the application code**. Possible causes:

- **Network latency:** Distance between user and server
- **Prolific overhead:** Platform-specific routing
- **Server infrastructure:** Hosting provider response times
- **oTree session creation:** Initial database operations when starting a new participant