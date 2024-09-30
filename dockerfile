FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

WORKDIR /

RUN apt-get update -y

RUN apt install --yes --no-install-recommends libopengl0 libcairo2-dev libjpeg-dev libgif-dev pkg-config

RUN pip install runpod huggingface_hub websocket-client cupy-cuda12x redis[hiredis] mutagen requests

COPY ./comfy_snapshot.json ./snapshot.json

COPY ./load_snapshot.py .

COPY ./extra_model_paths.yaml ./ComfyUI/extra_model_paths.yaml
RUN python load_snapshot.py

ENTRYPOINT ["python", "-u", "handler.py"]
