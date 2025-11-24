# 🔧 Sandbox Access Fix - Universal Secret Loading

## Problem

Some Cursor AI instances are **sandboxed** and can't access files outside the workspace (like `~/.config/secrets/global.env`), while others can. This causes inconsistent behavior.

## Solution

Use **workspace-relative secret loading** that works in both environments.

---

## ✅ Universal Secret Loader

### Python Usage

```python
from scripts.get_secret import get_secret

# Get a secret (tries multiple locations automatically)
api_key = get_secret('GOOGLE_MAPS_API_KEY')
snowflake_password = get_secret('SNOWFLAKE_PASSWORD')
```

**What it does:**
1. Checks environment variables first (highest priority)
2. Tries `~/.config/secrets/global.env` (if accessible)
3. Tries `.env` in project root (always accessible)
4. Returns default if not found

### Shell Script Usage

```bash
# Load secrets (works in both sandboxed and non-sandboxed)
source scripts/load_secrets.sh

# Now all secrets are available
echo $GOOGLE_MAPS_API_KEY
echo $SNOWFLAKE_PASSWORD
```

---

## 📁 Secret File Priority

The loaders try these locations **in order**:

1. **Environment variables** (already set)
2. `~/.config/secrets/global.env` (if accessible)
3. `~/.secrets/global.env` (alternative location)
4. `./.env` (project root - **always accessible**)
5. `./.env.local` (local overrides)

**First match wins!**

---

## 🔄 Migration Example

### Before (Breaks in Sandbox):
```python
# ❌ This fails in sandboxed environments
import os
with open(os.path.expanduser('~/.config/secrets/global.env')) as f:
    # ...
```

### After (Works Everywhere):
```python
# ✅ This works in both sandboxed and non-sandboxed
from scripts.get_secret import get_secret
api_key = get_secret('GOOGLE_MAPS_API_KEY')
```

---

## 🎯 For Cursor AI Assistants

**When accessing secrets, always use:**

```python
from scripts.get_secret import get_secret
```

**Never assume:**
- ❌ `~/.config/secrets/global.env` is accessible
- ❌ Filesystem access outside workspace
- ❌ Home directory access

**Always:**
- ✅ Use `scripts/get_secret.py`
- ✅ Check multiple locations
- ✅ Provide fallbacks
- ✅ Handle PermissionError gracefully

---

**Status:** ✅ Fixed - Works in both sandboxed and non-sandboxed environments


