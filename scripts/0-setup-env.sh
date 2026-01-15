#!/bin/bash

# ================= CONFIGURATION =================
PROJECT_ROOT="$(pwd)"
VENV_DIR="venv"

echo "🚀 Starting Environment Setup..."
echo "-------------------------------------------------------"

# 1. เช็คและสร้าง Python Virtual Environment
if [ -d "$VENV_DIR" ]; then
    echo "   ✅ Virtual environment '$VENV_DIR' already exists."
else
    echo "   📦 Creating virtual environment..."
    if command -v uv >/dev/null 2>&1; then
        uv venv "$VENV_DIR"
    else
        python3 -m venv "$VENV_DIR"
    fi
    echo "   ✅ Created '$VENV_DIR'."
fi

# 2. Activate Venv
source "$VENV_DIR/bin/activate"

# 3. Install Dependencies & Install Project (เพื่อให้ได้คำสั่ง cf-export)
echo "   ⬇️  Installing dependencies..."

if command -v uv >/dev/null 2>&1; then
    echo "      Using 'uv' to sync dependencies..."
    uv sync
else
    echo "      Using 'pip' to install..."
    pip install --upgrade pip
    
    # Install โปรเจคปัจจุบัน (.) ซึ่งจะอ่าน pyproject.toml 
    # และสร้างคำสั่ง cf-export ให้โดยอัตโนมัติ
    pip install -e .
fi

# 4. ตรวจสอบว่า cf-export ใช้งานได้ไหม
if command -v cf-export >/dev/null 2>&1; then
    echo "   ✅ Setup Complete! command 'cf-export' is ready."
else
    echo "   ❌ Error: 'cf-export' command not found. Installation failed."
    exit 1
fi

echo "-------------------------------------------------------"