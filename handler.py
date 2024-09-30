import json
import time
import requests
import runpod
import socket
import subprocess
import os


HOST = "127.0.0.1"
PORT = "8188"
COMFY_URL = f"{HOST}:{PORT}"


def start_comfy():
    cmd = [
        "python",
        "./ComfyUI/main.py",
        "--dont-print-server",
        "--disable-auto-launch",
        "--disable-metadata",
        "--listen",
        "--port",
        PORT,
    ]

    process = subprocess.Popen(
        cmd,
        text=True,
    )

    # Poll until webserver accepts connections before running inputs.
    while True:
        try:
            socket.create_connection((HOST, int(PORT)), timeout=1).close()
            print("ComfyUI Webserver Ready!")
            break
        except (socket.timeout, ConnectionRefusedError):
            retcode = process.poll()
            if retcode is not None:
                raise RuntimeError(
                    f"Comfyui main.py Exited Unexpectedly with Code: {retcode}"
                )


def queue_prompt(data):
    input = {"prompt": data["prompt"], "client_id": "kamikai"}
    serialized = json.dumps(input).encode("utf-8")
    req = requests.post(f"http://{COMFY_URL}/prompt", data=serialized)
    return req.json()


comfy_init_start = time.time() * 1000
start_comfy()
comfy_init_end = time.time() * 1000


def handler(job):
    CURRENT_JOB = job["input"]

    provider_metadata = {
        "gpu_count": os.environ.get("RUNPOD_GPU_COUNT", None),
        "cpu_count": os.environ.get("RUNPOD_CPU_COUNT", None),
        "mem_gb": os.environ.get("RUNPOD_MEM_GB", None),
        "gpu_name": os.environ.get("RUNPOD_GPU_NAME", None),
        "gpu_size": os.environ.get("RUNPOD_GPU_SIZE", None),
        "cuda_version": os.environ.get("CUDA_VERSION", None),
    }
    print(f"Provider Metadata: {json.dumps(provider_metadata)}")
    return {
        "provider_metadata": provider_metadata,
        "process_id": CURRENT_JOB["process_id"],
        "comfy_init_time": comfy_init_end - comfy_init_start,
        "comfy_init_start": comfy_init_start,
        "comfy_init_end": comfy_init_end,
        "refresh_worker": True,
    }


runpod.serverless.start({"handler": handler})
