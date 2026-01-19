#!/bin/bash
# start_chroma.sh for Native ChromaDB Service

# Activate Virtual Environment
source backend/venv/bin/activate

# Port 8001 to avoid conflict with API (8000)
PORT=8001
DB_PATH="./backend/chroma_db"

echo "🚀 Starting ChromaDB Server on port $PORT..."
echo "📂 Data Path: $DB_PATH"

# Run Chroma CLI
# Note: "chroma run" might need to be "chroma-cli run" or python -m chromadb.cli
# The standard command is 'chroma run' if installed via pip.

chroma run --path $DB_PATH --port $PORT
