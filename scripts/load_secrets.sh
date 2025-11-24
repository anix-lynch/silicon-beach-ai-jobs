#!/bin/bash
# 🔐 Universal Secret Loader
# Works in both sandboxed and non-sandboxed environments
# 
# Usage: source scripts/load_secrets.sh
# Or: eval $(scripts/load_secrets.sh)

# Try multiple secret locations (in order of preference)
SECRET_PATHS=(
    "$HOME/.config/secrets/global.env"
    "$HOME/.secrets/global.env"
    "./.env"
    "./.env.local"
    "../.env"
    "../.env.local"
)

# Function to safely source a file if it exists
load_secrets() {
    local file="$1"
    if [ -f "$file" ] && [ -r "$file" ]; then
        echo "# Loading secrets from: $file" >&2
        # Export all variables from the file
        set -a
        source "$file"
        set +a
        return 0
    fi
    return 1
}

# Try each path
for path in "${SECRET_PATHS[@]}"; do
    if load_secrets "$path"; then
        echo "# ✅ Secrets loaded from: $path" >&2
        exit 0
    fi
done

# If no secrets found, warn but don't fail
echo "# ⚠️  No secrets file found. Tried:" >&2
for path in "${SECRET_PATHS[@]}"; do
    echo "#   - $path" >&2
done
echo "# Create one of these files or set environment variables manually." >&2
exit 0

