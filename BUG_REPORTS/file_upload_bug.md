# File Upload Bug Report

**Date**: 2025-11-11
**Status**: BROKEN ❌
**Severity**: CRITICAL - Blocks optimization workflow

## Problem

The Task agent's file upload capability is **BROKEN**. When asked to upload files to QuantConnect:

1. Task agent reports "✅ Successfully uploaded"
2. But the file is **NOT actually uploaded**
3. This causes optimization to fail silently (all backtests use default parameters)

## Evidence

- Task agent claimed to upload `statistical_arbitrage.py` to project 26140717
- Verification showed the file was NOT uploaded
- User had to manually verify on QuantConnect web interface

## Root Cause

The Task agent does not have direct access to the QuantConnect API. It may be:
- Using a mock/simulated upload
- Not properly calling the real API methods
- Lacking credentials/authentication

## Working Workaround

Direct API calls using `qc_backtest.py` work:

```python
from qc_backtest import QuantConnectAPI
api = QuantConnectAPI()

# Delete old file
api._request('POST', 'files/delete', json={'projectId': project_id, 'name': 'main.py'})

# Create new file
api._request('POST', 'files/create', json={
    'projectId': project_id,
    'name': 'main.py',
    'content': code
})
```

## Impact

- **Cannot trust Task agent for file uploads**
- Must manually verify ALL uploads
- Wastes time with false success reports
- Blocks autonomous workflow

## Action Items for Next Session

1. ✅ Label Task agent upload skill as BROKEN
2. ⚠️ Always use direct API calls for uploads
3. ⚠️ Never trust Task agent "upload successful" messages
4. 🔧 Investigate why Task agent can't access real API
5. 🔧 Consider fixing Task agent or removing upload capability

## Related Issues

- Optimization silently failed (all results identical) because parameters weren't applied
- Root cause: old code on QC still had `getattr()` instead of `GetParameter()`
- Task agent falsely reported upload success

---

**NOTE TO FUTURE SESSIONS**: Do NOT use Task agent for file uploads to QuantConnect. Use direct API calls only.
