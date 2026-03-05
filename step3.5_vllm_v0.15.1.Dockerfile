FROM vllm/vllm-openai:v0.15.1-x86_64
COPY step3.5_vllm_v0.15.1.patch /usr/bin/patches/step3.5_vllm_v0.15.1.patch
RUN apt-get update && apt-get install -y git
RUN git -C /usr/local/lib/python3.12/dist-packages apply --exclude='tests/*' --exclude='examples/*' /usr/bin/patches/step3.5_vllm_v0.15.1.patch
