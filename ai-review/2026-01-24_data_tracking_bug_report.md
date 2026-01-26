# Bug Report: `work_seconds` Race Condition

## Status: FIXED (2026-01-25)

---

## Summary

`work_seconds` was lost when `liveSend` didn't complete before page reload. The hidden form field wasn't in `form_fields`, there was no sessionStorage backup, and `liveRecv` could overwrite restored values.

---

## Evidence

**Participant**: `cv66jt89` | **Session**: `x8jjzo5p`

| Task | actual | work_seconds | attention_received |
|------|--------|--------------|---------------------|
| 4    | 0      | 480          | 7                   |
| 5    | 0      | 480          | 7                   |

7 attention checks = 7min non-work, but `work_seconds = 480` (full timer).

---

## Root Cause Analysis

**Flow when "Stop Working" pressed:**

1. `stopWorking()` sets hidden field value
2. `liveSend()` sends via websocket (async, may not complete)
3. Page reloads after 1 second
4. Hidden field resets to server value (`{{ player.work_seconds }}`)
5. If liveSend failed -> server has 0 -> hidden field = 0
6. Form submits 0 -> `before_next_page` sets to total

**Additional issue identified by GPT Architect review:**

Even with sessionStorage backup, the `liveRecv` function unconditionally overwrote `work_seconds` from server responses, which could reset a correctly-restored value back to 0 before form submission.

**Why it worked for most participants:**

- liveSend usually completes in <1 second
- Only fails on network issues or slow connections

---

## Complete Fix (5 parts)

### 1. Add to form_fields (backup submission)

```python
# study/__init__.py, Task class
form_fields = ['performance', 'mistakes', 'work_seconds']
```

**Why:** Ensures oTree reads the hidden field value on form submission, providing a backup path if liveSend failed.

### 2. Add sessionStorage key

```javascript
// Task.html, after other STORAGE_KEY constants
const STORAGE_KEY_WORK = 'task_work_seconds_round_{{ player.round_number }}';
```

**Why:** Per-round key prevents cross-round contamination while allowing backup persistence.

### 3. Save before liveSend

```javascript
// Task.html, in stopWorking() before liveSend
setStoredValue(STORAGE_KEY_WORK, work);
```

**Why:** sessionStorage write is synchronous and completes before any async operation. Value is preserved even if page reloads immediately.

### 4. Restore on page load

```javascript
// Task.html, in DOMContentLoaded alongside perf/mistakes reconciliation
const storedWork = getStoredValue(STORAGE_KEY_WORK);
const serverWork = {{ player.work_seconds }};
const reconciledWork = Math.max(storedWork, serverWork);
document.getElementById("work_seconds").value = reconciledWork;
setStoredValue(STORAGE_KEY_WORK, reconciledWork);
```

**Why:** On page reload, compares sessionStorage (client truth) with server value and takes the max. Updates both the hidden field and sessionStorage with reconciled value.

### 5. Reconcile in liveRecv (CRITICAL)

```javascript
// Task.html, in liveRecv() where work_seconds is handled
if (typeof data.work_seconds === 'number') {
    const storedWork = getStoredValue(STORAGE_KEY_WORK);
    const reconciledWork = Math.max(storedWork, data.work_seconds);
    document.getElementById("work_seconds").value = reconciledWork;
    setStoredValue(STORAGE_KEY_WORK, reconciledWork);
}
```

**Why:** Server responses (from init, request_update, or other liveSend calls) could return `work_seconds=0` and overwrite the correctly-restored value. By reconciling with `Math.max()`, we ensure the client's known-good value is never lost.

---

## Why This Works

The fix creates multiple layers of protection:

1. **sessionStorage** survives page reload (synchronous write before any async)
2. **form_fields** ensures hidden field is submitted to server
3. **DOMContentLoaded reconciliation** restores value immediately on page load
4. **liveRecv reconciliation** prevents server responses from overwriting restored value
5. **Math.max()** strategy ensures we never lose a valid work time (work_seconds can only increase)

**Data flow with fix:**

```
stopWorking() clicked
    |
    v
[1] Set hidden field = work
[2] setStoredValue(STORAGE_KEY_WORK, work)  <- SYNC, guaranteed
[3] liveSend({stop_work: true, work_seconds: work})  <- ASYNC
    |
    v
Page reloads (liveSend may or may not complete)
    |
    v
DOMContentLoaded:
    - storedWork = getStoredValue() <- Has our value!
    - serverWork = {{ player.work_seconds }} <- May be 0
    - reconciledWork = Math.max(storedWork, serverWork) <- Our value wins
    |
    v
liveRecv (if server responds with work_seconds):
    - Reconcile again with Math.max() <- Still protected
    |
    v
Form submits:
    - work_seconds field has correct value
    - Server receives and stores correct value
```

---

## Files Modified

| File | Change |
|------|--------|
| `study/__init__.py` | Added `work_seconds` to Task.form_fields |
| `study/Task.html` | Added STORAGE_KEY_WORK constant |
| `study/Task.html` | Added setStoredValue in stopWorking() |
| `study/Task.html` | Added work_seconds reconciliation in DOMContentLoaded |
| `study/Task.html` | Added work_seconds reconciliation in liveRecv |
| `study/tests.py` | Updated bot to submit work_seconds in Task form |

---

## Testing

Bot tests pass with correct work_seconds tracking:
- Round 2: `work_seconds: 20` (early stop after 20s)
- Round 4: `work_seconds: 3` (early stop after 3s)
- Other rounds: `work_seconds: 120` (full timer)

---

## Data Recovery

For affected historical records:

```
estimated_work_seconds = total - (attention_checks_received * 60)
```

---

## Expert Review

**GPT Architect** identified the critical gap in liveRecv that the original 4-part fix missed.

**GPT Code Reviewer** approved the pattern as consistent with existing performance/mistakes backup system.
