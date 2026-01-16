#!/bin/bash

# สั่งให้ Script ทำงานในโฟลเดอร์ที่ไฟล์นี้อยู่
cd "$(dirname "$0")"

# 1. ถ้ายังไม่มี venv ให้รัน Setup ก่อน
if [ ! -d "venv" ]; then
    echo "⚙️  First time setup detected..."
    bash scripts/0-setup-env.sh
    
    # เช็คว่า Setup ผ่านไหม
    if [ $? -ne 0 ]; then
        echo "❌ Setup failed. Press any key to exit..."
        read -n 1
        exit 1
    fi
fi

# 2. Activate Venv
source venv/bin/activate

# 3. รัน UI
echo "🚀 Launching Migration Tool..."
streamlit run ui.py