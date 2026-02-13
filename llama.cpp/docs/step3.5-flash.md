## Step3.5-Flash

We support deploying **int4** quantized models on devices with **128GB unified memory**, enabling a GPT-OSS-120B–comparable model experience on personal workstations while significantly reducing inference cost and latency.

The currently validated platforms include:

* **Mac Studio M4 Max**
* **NVIDIA DGX-Spark**
* **AMD Ryzen AI Max+ 395 (Windows)**

---

### Prepare Model and Code

Download the Q4_K_S quantized GGUF weight file [Step3.5-Flash](https://huggingface.co/stepfun-ai/Step-3.5-Flash-Int4/tree/main), which can be used directly for on-device inference.

Use llama.cpp:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

---

### Using Step3.5-Flash on Mac

Build llama.cpp with `CMake`:

```bash
cmake -S . -B build-macos \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_METAL=ON \
  -DGGML_ACCELERATE=ON \
  -DLLAMA_BUILD_EXAMPLES=ON \
  -DLLAMA_BUILD_COMMON=ON \
  -DGGML_LTO=ON
cmake --build build-macos -j8
```

Basic inference command:

```bash
./llama-cli -m step3.5_flash_Q4_K_S.gguf -c 16384 -b 2048 -ub 2048 -fa on --temp 1.0 -p "What's your name?"
```

Performance benchmark command:

```bash
./llama-batched-bench -m .step3.5_flash_Q4_K_S.gguf -c 16384 -b 2048 -ub 2048 -npp 0,2048,8192,16384 -ntg 128 -npl 1
```

Note: Due to [memory limitations on Apple silicon](https://stencel.io/posts/apple-silicon-limitations-with-usage-on-local-llm%20.html), testing long context requires increasing the available memory to 120GB using the following command. With `-ub 1024`, up to a 256K context can be run:

```bash
sudo sysctl iogpu.wired_limit_mb=122880
```

Alternatively, for contexts not exceeding 76K, you can increase runtime parameters to enable KV cache quantization, at the cost of some precision:

```bash
-ctk q8_0 -ctv q8_0
```

The performance benchmark results are as follows:

```bash
./llama-batched-bench -m step3.5_flash_Q4_K_S.gguf -c 262150 -b 2048 -ub 1024 -npp 0,2048,8192,16384,32768,65536,262144 -ntg 128 -npl 1
```

| PP     | TG  | B | N_KV   | T_PP (s) | S_PP (t/s) | T_TG (s) | S_TG (t/s) | T (s)    | S (t/s) |
| ------ | --- | - | ------ | -------- | ---------- | -------- | ---------- | -------- | ------- |
| 0      | 128 | 1 | 128    | 0.000    | 0.00       | 2.657    | 48.18      | 2.657    | 48.18   |
| 2048   | 128 | 1 | 2176   | 5.040    | 406.35     | 2.785    | 45.96      | 7.825    | 278.08  |
| 8192   | 128 | 1 | 8320   | 20.923   | 391.52     | 2.916    | 43.90      | 23.839   | 349.01  |
| 16384  | 128 | 1 | 16512  | 43.982   | 372.52     | 3.102    | 41.27      | 47.083   | 350.70  |
| 32768  | 128 | 1 | 32896  | 97.454   | 336.24     | 3.349    | 38.22      | 100.803  | 326.34  |
| 65536  | 128 | 1 | 65664  | 239.381  | 273.77     | 4.060    | 31.52      | 243.441  | 269.73  |
| 262144 | 128 | 1 | 262272 | 2193.455 | 119.51     | 14.409   | 8.88       | 2207.864 | 118.79  |

---

### Using Step3.5-Flash on DGX-Spark

Build llama.cpp with `CMake`:

```bash
cmake -S . -B build-cuda \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_CUDA=ON \
  -DGGML_CUDA_GRAPHS=ON \
  -DLLAMA_CURL=OFF \
  -DLLAMA_BUILD_EXAMPLES=ON \
  -DLLAMA_BUILD_COMMON=ON
cmake --build build-cuda -j8
```

Basic inference command:

```bash
./llama-cli -m step3.5_flash_Q4_K_S.gguf -c 16384 -b 2048 -ub 2048 -fa on --temp 1.0 -p "What's your name?"
```

Performance benchmark command:

```bash
./llama-batched-bench -m step3.5_flash_Q4_K_S.gguf -c 16384 -b 2048 -ub 2048 -npp 0,2048,8192,16384 -ntg 128 -npl 1
```

When testing long context (e.g. 256K), OOM may occur. The build flag `-DGGML_CUDA_FORCE_MMQ=ON`, environment variable `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1`, and runtime parameters `-ctk q8_0 -ctv q8_0` can help mitigate memory issues. You can also use the following command to [clear memory cache](https://forums.developer.nvidia.com/t/dgx-spark-gb10-faq/347344):

```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```

The performance benchmark results are as follows:

```bash
GGML_CUDA_ENABLE_UNIFIED_MEMORY=1 ./llama-batched-bench -m step3.5_flash_Q4_K_S.gguf -c 262150 -b 2048 -ub 1024 -npp 0,2048,8192,16384,32768,65536,262144 -ntg 128 -npl 1 -ctk q8_0 -ctv q8_0
```

| PP     | TG  | B | N_KV   | T_PP (s) | S_PP (t/s) | T_TG (s) | S_TG (t/s) | T (s)    | S (t/s) |
| ------ | --- | - | ------ | -------- | ---------- | -------- | ---------- | -------- | ------- |
| 0      | 128 | 1 | 128    | 0.000    | 0.00       | 6.468    | 19.79      | 6.468    | 19.79   |
| 2048   | 128 | 1 | 2176   | 5.222    | 392.17     | 6.315    | 20.27      | 11.538   | 188.60  |
| 8192   | 128 | 1 | 8320   | 15.341   | 533.99     | 6.321    | 20.25      | 21.662   | 384.08  |
| 16384  | 128 | 1 | 16512  | 31.008   | 528.39     | 6.652    | 19.24      | 37.659   | 438.46  |
| 32768  | 128 | 1 | 32896  | 68.606   | 477.63     | 7.210    | 17.75      | 75.816   | 433.89  |
| 65536  | 128 | 1 | 65664  | 167.820  | 390.51     | 8.303    | 15.42      | 176.122  | 372.83  |
| 262144 | 128 | 1 | 262272 | 1206.853 | 217.21     | 15.265   | 8.39       | 1222.118 | 214.60  |

---

### Using Step3.5-Flash on AMD Ryzen AI Max+ 395

Build llama.cpp with `CMake` (Vulkan-SDK must be installed in advance):

```bash
cmake -S . -B build-vulkan \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_CURL=OFF \
  -DGGML_OPENMP=ON \
  -DGGML_VULKAN=ON
cmake --build build-vulkan -j8
```

Basic inference command:

```bash
llama-cli.exe -m step3.5_flash_Q4_K_S.gguf -c 16384 -b 2048 -ub 2048 -fa on --temp 1.0 -p "What's your name?"
```

Performance benchmark command:

```bash
llama-batched-bench.exe -m step3.5_flash_Q4_K_S.gguf -c 16384 -b 2048 -ub 2048 -npp 0,2048,8192,16384 -ntg 128 -npl 1
```

The performance benchmark results are as follows:

```bash
llama-batched-bench.exe -m step3p5_flash_Q4_K_S.gguf -c 65540 -b 2048 -ub 2048 -npp 0,2048,8192,16384,32768,65536 -ntg 128 -npl 1 --mmap -t 32
```

| PP    | TG  | B | N_KV  | T_PP (s) | S_PP (t/s) | T_TG (s) | S_TG (t/s) | T (s)    | S (t/s) |
| ----- | --- | - | ----- | -------- | ---------- | -------- | ---------- | -------- | ------- |
| 0     | 128 | 1 | 128   | 0.000    | 0.00       | 37.337   | 3.43       | 37.337   | 3.43    |
| 2048  | 128 | 1 | 2176  | 10.346   | 197.94     | 37.620   | 3.40       | 47.967   | 45.36   |
| 8192  | 128 | 1 | 8320  | 47.678   | 171.82     | 38.127   | 3.36       | 85.805   | 96.96   |
| 16384 | 128 | 1 | 16512 | 124.570  | 131.52     | 38.773   | 3.30       | 164.343  | 101.09  |
| 32768 | 128 | 1 | 32896 | 395.684  | 82.81      | 40.170   | 3.19       | 435.854  | 75.47   |
| 65536 | 128 | 1 | 65664 | 1520.696 | 43.10      | 43.014   | 2.98       | 1563.710 | 41.99   |

---

**TODO**:

* Further improve quantization quality using higher-quality calibration datasets
* Increase maximum context length and inference speed on AMD platforms
* Add MTP support

We welcome questions and suggestions—let’s work together to continuously improve the private deployment experience of large language models.
