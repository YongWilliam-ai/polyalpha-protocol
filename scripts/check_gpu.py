"""
check_gpu.py -- PolyAlpha GPU Availability Check (HKUST ugcpu1)

Runs nvidia-smi and reports which GPUs are available.
Known issue on ugcpu1: GPU3 occasionally shows 'Unknown Error' -- this
script treats that as a warning and continues on CPU.

Called by daily_runner.py startup check.
Returns 0 if at least one GPU is usable, 1 if all GPUs are unavailable.
"""

import subprocess
import sys
import logging

log = logging.getLogger("check_gpu")


def check_gpu() -> dict:
    """
    Run nvidia-smi and parse output.
    Returns {"available": bool, "gpus": list[dict], "warning": str|None}
    """
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,memory.used,memory.total,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10,
        )
    except FileNotFoundError:
        return {"available": False, "gpus": [], "warning": "nvidia-smi not found -- running on CPU"}
    except subprocess.TimeoutExpired:
        return {"available": False, "gpus": [], "warning": "nvidia-smi timed out"}
    except Exception as exc:
        return {"available": False, "gpus": [], "warning": str(exc)}

    if result.returncode != 0:
        stderr = result.stderr.strip()
        # Known ugcpu1 issue: GPU3 Unknown Error
        if "Unknown Error" in stderr:
            warning = f"GPU(s) show 'Unknown Error' (known ugcpu1 issue) -- falling back to CPU. stderr: {stderr}"
            log.warning(warning)
            return {"available": False, "gpus": [], "warning": warning}
        return {"available": False, "gpus": [], "warning": f"nvidia-smi error: {stderr}"}

    gpus = []
    for line in result.stdout.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 5:
            try:
                gpus.append({
                    "index":        int(parts[0]),
                    "name":         parts[1],
                    "mem_used_mb":  int(parts[2]),
                    "mem_total_mb": int(parts[3]),
                    "utilization":  int(parts[4]),
                })
            except (ValueError, IndexError):
                pass

    available = len(gpus) > 0
    return {"available": available, "gpus": gpus, "warning": None}


def print_report(info: dict) -> None:
    if info["warning"]:
        print(f"GPU WARNING: {info['warning']}")
    if info["gpus"]:
        print(f"GPUs available: {len(info['gpus'])}")
        for g in info["gpus"]:
            pct = round(g["mem_used_mb"] / g["mem_total_mb"] * 100) if g["mem_total_mb"] else 0
            print(
                f"  GPU{g['index']}: {g['name']} | "
                f"Mem: {g['mem_used_mb']}/{g['mem_total_mb']} MB ({pct}%) | "
                f"Util: {g['utilization']}%"
            )
    else:
        print("No GPUs detected -- daily_runner will use CPU (no impact on scanner performance)")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    info = check_gpu()
    print_report(info)
    sys.exit(0 if info["available"] else 1)
