#!/bin/bash

# Skip on first create — setup_runtime.sh already started Oracle.
if [ -f /tmp/.oracle_setup_done ]; then
  echo "[oracle] First-create setup already ran. Checking Oracle state..."
  rm -f /tmp/.oracle_setup_done
else
  echo "[oracle] Container restart detected. Starting Oracle..."
fi

echo "[oracle] Waiting for Docker daemon..."
for i in $(seq 1 10); do
  docker info > /dev/null 2>&1 && echo "[oracle] Docker is ready." && break \
    || { [ $i -lt 10 ] && sleep 2; }
done

echo "[oracle] Starting Oracle AI Database..."
docker compose -f .devcontainer/docker-compose.yml start oracle 2>/dev/null \
  || docker compose -f .devcontainer/docker-compose.yml up -d oracle

echo "[oracle] Waiting for Oracle to accept connections..."
for i in $(seq 1 15); do
  python3 -c "
import oracledb, sys
try:
    c = oracledb.connect(user='sys', password='OraclePwd_2025', dsn='localhost:1521/FREE', mode=oracledb.SYSDBA)
    c.close()
    sys.exit(0)
except:
    sys.exit(1)
" && break || sleep 5
done

# Check actual Vector Memory Area allocation in SGA (not just the parameter value).
# If VMA is not allocated, set SPFILE and restart.
python3 << 'PYEOF'
import oracledb, sys, subprocess, time

def connect_sysdba():
    return oracledb.connect(
        user="sys",
        password="OraclePwd_2025",
        dsn="localhost:1521/FREE",
        mode=oracledb.SYSDBA
    )

def get_vector_memory(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT current_size FROM v$sga_dynamic_components
        WHERE component = 'Vector Memory Area'
    """)
    row = cur.fetchone()
    return int(row[0]) if row else 0

try:
    conn = connect_sysdba()
except Exception:
    print("[oracle] Could not connect as SYSDBA — skipping VMA check")
    sys.exit(0)

actual_vma = get_vector_memory(conn)
if actual_vma >= 1073741824:
    print(f"[oracle] Vector Memory Area OK: {actual_vma // (1024**2)}M")
    conn.close()
    sys.exit(0)

print(f"[oracle] Vector Memory Area = {actual_vma // (1024**2)}M — fixing via SPFILE + restart...")

cur = conn.cursor()
try:
    cur.execute("ALTER SYSTEM SET vector_memory_size = 1G SCOPE=SPFILE")
    conn.commit()
    print("[oracle] Written vector_memory_size = 1G to SPFILE")
except Exception as e:
    print(f"[oracle] ERROR setting SPFILE: {e}")
    conn.close()
    sys.exit(1)

conn.close()

result = subprocess.run(["docker", "restart", "oracle-free"], capture_output=True, text=True)
if result.returncode != 0:
    print(f"[oracle] ERROR: docker restart failed: {result.stderr}")
    sys.exit(1)

print("[oracle] Waiting for Oracle to restart with VMA allocated...")
for attempt in range(1, 16):
    time.sleep(5)
    try:
        conn = connect_sysdba()
        actual_vma = get_vector_memory(conn)
        conn.close()
        if actual_vma >= 1073741824:
            print(f"[oracle] Confirmed: Vector Memory Area = {actual_vma // (1024**2)}M")
            sys.exit(0)
    except Exception:
        pass

print("[oracle] WARNING: Vector Memory Area may not be allocated")
sys.exit(1)
PYEOF

echo "[oracle] Oracle container started."
