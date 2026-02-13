## Step3.5-Flash
我们支持将 **int4** 量化后的模型部署到有 **128GB** 统一内存的设备上，通过个人工作站获得对标 gpt-oss-120B 的模型体验并显著降低推理成本与延迟。

当前已验证的平台包括：

* **Mac Studio M4 Max**
* **NVIDIA DGX-Spark**
* **AMD Ryzen AI Max+ 395（window系统）**

---

### 准备模型和代码
下载 Q4_K_S 量化版本的 GGUF 权重文件 [Step3.5-Flash](https://huggingface.co/stepfun-ai/Step-3.5-Flash-Int4/tree/main) ，可直接用于端侧设备推理.

Use llama.cpp:
```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

---

### 在 Mac 上使用 Step3.5-Flash
使用 `CMake` 编译 llama.cpp:
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
基础推理命令：
```bash
./llama-cli -m step3.5_flash_Q4_K_S.gguf -c 16384 -b 2048 -ub 2048 -fa on --temp 1.0 -p "What's your name?"
```
性能测试命令：
```bash
./llama-batched-bench -m .step3.5_flash_Q4_K_S.gguf -c 16384 -b 2048 -ub 2048 -npp 0,2048,8192,16384 -ntg 128 -npl 1
```
注意：由于 Apple silicon 有[内存限制](https://stencel.io/posts/apple-silicon-limitations-with-usage-on-local-llm%20.html)，如果想测试长上下文，需要通过以下命令来将可用内存提高到120GB，在设置 -ub 1024 的情况下最高可运行 256k 上下文
```bash
sudo sysctl iogpu.wired_limit_mb=122880
```
或者在不超过 76K 上下文的情况下增加运行时参数进行 kv cache 量化，但可能会牺牲部分精度
```bash
-ctk q8_0 -ctv q8_0
```
性能测试的 BenchMark 如下：
```bash
./llama-batched-bench -m step3.5_flash_Q4_K_S.gguf -c 262150 -b 2048 -ub 1024 -npp 0,2048,8192,16384,32768,65536,262144 -ntg 128 -npl 1
```
| PP     | TG  | B | N_KV   | T_PP (s) | S_PP (t/s) | T_TG (s) | S_TG (t/s) | T (s)   | S (t/s) |
|--------|-----|---|--------|----------|------------|----------|------------|---------|----------|
| 0      | 128 | 1 | 128    | 0.000    | 0.00       | 2.657    | 48.18      | 2.657   | 48.18    |
| 2048   | 128 | 1 | 2176   | 5.040    | 406.35     | 2.785    | 45.96      | 7.825   | 278.08   |
| 8192   | 128 | 1 | 8320   | 20.923   | 391.52     | 2.916    | 43.90      | 23.839  | 349.01   |
| 16384  | 128 | 1 | 16512  | 43.982   | 372.52     | 3.102    | 41.27      | 47.083  | 350.70   |
| 32768  | 128 | 1 | 32896  | 97.454   | 336.24     | 3.349    | 38.22      | 100.803 | 326.34   |
| 65536  | 128 | 1 | 65664  | 239.381  | 273.77     | 4.060    | 31.52      | 243.441 | 269.73   |
| 262144 | 128 | 1 | 262272 | 2193.455 | 119.51     | 14.409   | 8.88       | 2207.864| 118.79   |


---

### 在 DGX-Spark 上使用 Step3.5-Flash
使用 `CMake` 编译 llama.cpp:
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
基础推理命令：
```bash
./llama-cli -m step3.5_flash_Q4_K_S.gguf -c 16384 -b 2048 -ub 2048 -fa on --temp 1.0 -p "What's your name?"
```
性能测试命令：
```bash
./llama-batched-bench -m step3.5_flash_Q4_K_S.gguf -c 16384 -b 2048 -ub 2048 -npp 0,2048,8192,16384 -ntg 128 -npl 1
```
如果想测试长上下文（例如 256K）可能会出现OOM，编译参数 -DGGML_CUDA_FORCE_MMQ=ON 、环境变量 GGML_CUDA_ENABLE_UNIFIED_MEMORY=1 以及运行时参数 -ctk q8_0 -ctv q8_0 可以用于缓解内存问题。同时可以用以下命令 [清理内存cache](https://forums.developer.nvidia.com/t/dgx-spark-gb10-faq/347344)
```bash
sudo sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'
```
性能测试的 BenchMark 如下：
```bash
GGML_CUDA_ENABLE_UNIFIED_MEMORY=1 ./llama-batched-bench -m step3.5_flash_Q4_K_S.gguf -c 262150 -b 2048 -ub 1024 -npp 0,2048,8192,16384,32768,65536,262144 -ntg 128 -npl 1 -ctk q8_0 -ctv q8_0
```
| PP     | TG  | B | N_KV   | T_PP (s) | S_PP (t/s) | T_TG (s) | S_TG (t/s) | T (s)   | S (t/s) |
|--------|-----|---|--------|----------|------------|----------|------------|---------|----------|
| 0      | 128 | 1 | 128    | 0.000    | 0.00       | 6.468    | 19.79      | 6.468   | 19.79    |
| 2048   | 128 | 1 | 2176   | 5.222    | 392.17     | 6.315    | 20.27      | 11.538  | 188.60   |
| 8192   | 128 | 1 | 8320   | 15.341   | 533.99     | 6.321    | 20.25      | 21.662  | 384.08   |
| 16384  | 128 | 1 | 16512  | 31.008   | 528.39     | 6.652    | 19.24      | 37.659  | 438.46   |
| 32768  | 128 | 1 | 32896  | 68.606   | 477.63     | 7.210    | 17.75      | 75.816  | 433.89   |
| 65536  | 128 | 1 | 65664  | 167.820  | 390.51     | 8.303    | 15.42      | 176.122 | 372.83   |
| 262144 | 128 | 1 | 262272 | 1206.853 | 217.21     | 15.265   | 8.39       | 1222.118| 214.60   |


---

### 在 AMD Ryzen AI Max+ 395 上使用 Step3.5-Flash
使用 `CMake` 编译 llama.cpp（需要预先安装Vulkan-SDK）:
```bash
cmake -S . -B build-vulkan \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_CURL=OFF \
  -DGGML_OPENMP=ON \
  -DGGML_VULKAN=ON
cmake --build build-vulkan -j8
```
基础推理命令：
```bash
llama-cli.exe -m step3.5_flash_Q4_K_S.gguf -c 16384 -b 2048 -ub 2048 -fa on --temp 1.0 -p "What's your name?"
```
性能测试命令：
```bash
llama-batched-bench.exe -m step3.5_flash_Q4_K_S.gguf -c 16384 -b 2048 -ub 2048 -npp 0,2048,8192,16384 -ntg 128 -npl 1
```
性能测试的 BenchMark 如下：
```bash
llama-batched-bench.exe -m step3p5_flash_Q4_K_S.gguf -c 65540 -b 2048 -ub 2048 -npp 0,2048,8192,16384,32768,65536 -ntg 128 -npl 1 --mmap -t 32
```
| PP     | TG  | B | N_KV   | T_PP (s) | S_PP (t/s) | T_TG (s) | S_TG (t/s) | T (s)   | S (t/s) |
|--------|-----|---|--------|----------|------------|----------|------------|---------|----------|
| 0      | 128 | 1 | 128    | 0.000    | 0.00       | 37.337   | 3.43       | 37.337  | 3.43     |
| 2048   | 128 | 1 | 2176   | 10.346   | 197.94     | 37.620   | 3.40       | 47.967  | 45.36    |
| 8192   | 128 | 1 | 8320   | 47.678   | 171.82     | 38.127   | 3.36       | 85.805  | 96.96    |
| 16384  | 128 | 1 | 16512  | 124.570  | 131.52     | 38.773   | 3.30       | 164.343 | 101.09   |
| 32768  | 128 | 1 | 32896  | 395.684  | 82.81      | 40.170   | 3.19       | 435.854 | 75.47    |
| 65536  | 128 | 1 | 65664  | 1520.696 | 43.10      | 43.014   | 2.98       | 1563.710| 41.99    |

---

**TODO**:
 - 进一步提高量化质量，使用更高质量的量化校准集
 - 提升AMD机型的最大上下文和推理速度
 - 支持MTP
 
欢迎向我们提出问题与建议，一起让大语言模型私有化部署的体验越来越好！