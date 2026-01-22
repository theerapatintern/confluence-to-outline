#!/bin/bash
set -euo pipefail

# ================= CONFIGURATION =================
ENV_FILE="workspace/.env"

if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "Warning: .env file not found."
fi

TARGET_FILE="${1:-${INPUT_FILE:-workspace/url_list.txt}}"

# ================= VALIDATION =================
if [ ! -f "$TARGET_FILE" ]; then
    echo "Error: ไม่พบไฟล์ '$TARGET_FILE'"
    echo "กรุณาตรวจสอบไฟล์ .env หรือระบุชื่อไฟล์"
    exit 1
fi

echo "Processing file: $TARGET_FILE"

# ================= MAIN LOGIC =================
TMP_FILE="$(mktemp)"
COUNT_KEPT=0
COUNT_REMOVED=0

while IFS= read -r line || [ -n "$line" ]; do
    # ตัดช่องว่างหน้าหลังออกก่อน (Trim)
    clean_line=$(echo "$line" | xargs)

    # 1. เช็คว่าเป็นเลข 9 หลักเพียวๆ หรือไม่ (ถ้าใช่ ให้เก็บไว้เลย)
    if [[ "$clean_line" =~ ^[0-9]{9}$ ]]; then
        echo "$clean_line" >> "$TMP_FILE"
        COUNT_KEPT=$((COUNT_KEPT + 1))
        continue # ข้ามไปบรรทัดถัดไปทันที
    fi

    # 2. ถ้าไม่ใช่เลขเพียวๆ ให้ลองหา Pattern /pages/xxxx
    ids="$(printf '%s\n' "$line" | grep -oE '/pages/[0-9]+' || true)"
    ids="${ids#/pages/}"

    if [ -n "$ids" ]; then
        # เจอ ID ใน URL -> เก็บ
        echo "$ids" >> "$TMP_FILE"
        COUNT_KEPT=$((COUNT_KEPT + 1))
    else
        # ไม่ใช่เลข 9 หลัก และไม่เจอ /pages/ -> ตัดทิ้ง
        COUNT_REMOVED=$((COUNT_REMOVED + 1))
    fi

done < "$TARGET_FILE"

mv "$TMP_FILE" "$TARGET_FILE"

echo "Done: $TARGET_FILE"
echo "  - Valid IDs: $COUNT_KEPT"
echo "  - Removed lines: $COUNT_REMOVED"