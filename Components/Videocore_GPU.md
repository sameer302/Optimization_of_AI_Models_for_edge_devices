1) VideoCore VII GPU supports OpenGL ES 3.1, Vulkan 1.2. Both these API's are specifically for graphics and video rendering and not optimized to run general purpose AIML operations.

2) The Raspberry Pi 5’s VideoCore VII GPU does not support CUDA, and since modern AI/ML frameworks depend on CUDA for GPU acceleration, AI inference cannot be offloaded to the GPU and must run on the CPU or an external accelerator.

3) CUDA stands for Compute Unified Device Architecture and it is supported only by NVIDIA GPU's