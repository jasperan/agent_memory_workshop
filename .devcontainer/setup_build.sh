#!/bin/bash
set -e

echo "============================================"
echo "  Oracle Agent Memory Workshop - Build"
echo "============================================"

echo ""
echo "[1/3] Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo ""
echo "[2/3] Installing Python dependencies..."
pip install -q --no-cache-dir \
  langchain-oracledb \
  langchain-community \
  langchain-huggingface \
  langchain \
  sentence-transformers \
  oracledb \
  openai \
  tavily-python \
  datasets \
  jupyter \
  ipykernel \
  ipywidgets \
  matplotlib \
  requests \
  pydantic

echo ""
echo "[3/3] Registering Jupyter kernel..."
python -m ipykernel install --user --name workshop --display-name "Oracle Agent Memory Workshop"

echo ""
echo "Build complete. Oracle will start when the Codespace opens."
echo "============================================"
