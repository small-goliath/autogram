#!/bin/bash

# Check if correct number of arguments provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <login_username> <target_username>"
    exit 1
fi

LOGIN_USER=$1
TARGET_USER=$2

# Calculate date from 7 days ago
YEAR=$(date -v-7d +%Y)
MONTH=$(date -v-7d +%m)
DAY=$(date -v-7d +%d)

# Remove leading zeros (datetime expects integers)
MONTH=$((10#$MONTH))
DAY=$((10#$DAY))

# Create post-filter string
FILTER="date_utc >= datetime($YEAR, $MONTH, $DAY)"

echo "Downloading comments from @$TARGET_USER's posts from the last 7 days..."
echo "Login as: @$LOGIN_USER"
echo "Filter: $FILTER"

# Run instaloader with post-filter to download only comments from recent posts
# Monitor output and stop if "skipped" appears 4 times
SKIP_COUNT=0
instaloader --login "$LOGIN_USER" \
            --comments \
            --no-pictures \
            --no-videos \
            --no-video-thumbnails \
            --no-profile-pic \
            --post-filter="$FILTER" \
            profile "$TARGET_USER" 2>&1 | while IFS= read -r line; do
    echo "$line"

    if echo "$line" | grep -qi "skipped"; then
        SKIP_COUNT=$((SKIP_COUNT + 1))
        echo "[Skip count: $SKIP_COUNT/4]"

        if [ $SKIP_COUNT -ge 4 ]; then
            echo "Detected 4 skipped posts. Stopping download..."
            pkill -P $$ instaloader
            break
        fi
    fi
done

echo "Download complete!"
