# 🔐 Admin: Reset Snowflake Password

**Account:** ITB97131  
**User:** ANIXLYNCH

## Steps to Reset Password

### 1. **Log into Snowflake Admin Console**
- Go to: https://app.snowflake.com/
- Log in with your admin account

### 2. **Navigate to User Management**
1. Click **"Admin"** in the left sidebar
2. Click **"Users & Roles"**
3. Find user: **ANIXLYNCH**
4. Click on the user name

### 3. **Re-enable Password Authentication**
1. In the user details page, look for **"Authentication"** section
2. Find **"Password"** authentication method
3. Click **"Enable"** or **"Re-enable"** button
4. This will allow password sign-in again

### 4. **Reset the Password**
You have two options:

#### Option A: Reset via Admin UI (Recommended)
1. In the user details page, click **"Reset Password"** button
2. Snowflake will generate a temporary password
3. **Copy this password immediately** (you'll need it)
4. User will be forced to change it on next login

#### Option B: Set New Password Directly
1. In user details, click **"Edit"**
2. Scroll to **"Password"** section
3. Click **"Set Password"**
4. Enter a new strong password
5. Save changes

### 5. **Update Your Secret Files**

After setting the new password, update:

```bash
# Edit this file:
~/.config/secrets/global.env

# Update this line:
SNOWFLAKE_PASSWORD=your_new_password_here
```

### 6. **Test Connection**

```bash
cd /Users/anixlynch/dev/5miles-job-search
python3 -c "
from scripts.get_secret import get_secret
import snowflake.connector

config = {
    'account': get_secret('SNOWFLAKE_ACCOUNT', 'vwyiycr-rpb51995'),
    'user': get_secret('SNOWFLAKE_USER', 'ANIXLYNCH'),
    'password': get_secret('SNOWFLAKE_PASSWORD'),
    'database': get_secret('SNOWFLAKE_DATABASE', 'JOB_SEARCH'),
    'warehouse': get_secret('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
}

try:
    conn = snowflake.connector.connect(**config)
    print('✅ Connection successful with new password!')
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

## Alternative: SQL Commands (if UI doesn't work)

If you prefer SQL, run these in Snowflake worksheet:

```sql
-- Re-enable password authentication
ALTER USER ANIXLYNCH SET DISABLED = FALSE;

-- Reset password (user will be forced to change on next login)
ALTER USER ANIXLYNCH SET PASSWORD = 'TemporaryPassword123!';

-- Or set permanent password directly
ALTER USER ANIXLYNCH SET PASSWORD = 'YourNewStrongPassword123!';
```

## Security Best Practices

- ✅ Use a strong password (12+ characters, mixed case, numbers, symbols)
- ✅ Update password in secret files immediately
- ✅ Don't share password in plain text
- ✅ Consider using key pair authentication for production

## ✅ Checklist

- [ ] Logged into Snowflake as admin
- [ ] Re-enabled password authentication for ANIXLYNCH
- [ ] Reset/set new password
- [ ] Updated `~/.config/secrets/global.env`
- [ ] Tested connection successfully
- [ ] Updated Streamlit Cloud secrets (if deployed)

