## Running yolo11n pytorch model inference on CPU

- Here we are deciding the input resolution at which camera captures frames and also the resolution at which model runs its inference, by giving the argument `--capture-resolution`
- Here the batch size is implicitly set to 1 in the code and it makes sense because for live camera feed if we set batch size larger than 1 then we need to accumulate frames which will lead to latency. 
- while performing experiment and also while running benchmarking code we need to make sure that the input resolution and batch size is kept same so that we can have fair comparison

1) temperature_vs_time:-
    - https://www.raspberrypi.com/documentation/computers/config_txt.html#raspberry-pi-4:~:text=Monitoring%20core%20temperature 
    - When the core temperature is between 80°C and 85°C, the Arm cores will be throttled back. If the temperature exceeds 85°C, the Arm cores and the GPU will be throttled back.
    - For the Raspberry Pi 3 Model B+, when the soft limit is reached, the clock speed is reduced from 1.4 GHz to 1.2 GHz, and the operating voltage is reduced slightly. This reduces the rate of temperature increase: we trade a short period at 1.4 GHz for a longer period at 1.2 GHz. By default, the soft limit is 60°C. This can be changed via the temp_soft_limit setting in config.txt.
    - For Raspberry Pi 5, the exact temperature for soft limit and hard limit is not specifically mentioned but it can be found out experimentally by running some stress code  such as `stress-ng --cpu 4 --timeout 600` 
    - Due to this we can see that the temperature gets settled around 60 degree celsius, cpu frequency stayed constant at it's maximum capacity of 2.4 GHz and no throttling flags were shown.
    
2) cpu_frequency_vs_time:-
    - as per product sheet raspberry pi 5 has BCM2712 processor which operates at 2.4GHz max frequency normally and this frequency will be reduced in case of thermal throttling. 
    - but as in our case there was no thermal throttling hence the cpu frequency stayed constant. 

3) cpu_percentage_vs_time:-
    - here we can see that our code is using nearly 60% of CPU and whatever results we are observing are just with this 60% utilization. Also this is not just the utilization by our program but overall utilization which includes OS and other processes also utilizing CPU
    - There can be various reasons behind this and we may see if we can increase this utiliztion and whether that will increase the fps speed that we are obtaining. 

4) memory_percent_vs_time:-
    - here we can see that our program used nearly 28% of RAM and this is not just used by our program but it's overall usage so it includes OS and other processes utilization also. 
    - One reason why this is less is because our model is very small and if we were to use a larger model or higher input resolution then we will have more memory usage.

5) cpu_voltage_vs_time:- 
    - here the voltage we are measuring is the voltage drawn by CPU core. The voltage drawn by board is different and then each component internally has their own share of voltage to operate on.
    - we can measure the voltage drawn by the board using the command `vcgencmd pmic_read_adc EXT5V_V`
    - This voltage reading can help us to visualize whether we have throttling or not. If the overall CPU voltage has dropped then each individual component voltage will also be dropped and hence it confirms throttling. 
    - There are two types of throttling, thermal throttling and power throttling. 
    - In thermal throttling due to increase in temperature the cpu frequency and cpu core voltage is dropped in order to bring down the temperature. 
    - In power throttling (under-voltage) due to drop in input voltage the cpu frequency and cpu core voltage is dropped in order to adjust to the drop in input voltage. 
    - We can see the difference between both by looking at the throttle flags. We will have different flags for thermal throttling and power throttling. 
    - CPU voltage drawn stayed constant here indicating that there was no event of thermal or power throttling 

6) throttle_flags_vs_time:-
    - this is a firmware utility provided by the Raspberry Pi firmware, not directly by the OS or by user software. 
    - here we can see that no throttle flag was set during the entire inference timeline. 
    - This indicates there was no event of throttling neither due to thermal throttling nor due to power throttling. 
    - Throttling status can be understood by looking at the flags index given on the official website https://www.raspberrypi.com/documentation/computers/os.html#get_throttled  
    - We didnt see any throttle flags which means that the soft limit is well above 60 degree celsius. 

7) fps_vs_time:-
    - the fps speed that we obtained here is with respect to a particular input resolution. 
    - in our code we are giving two arguments, one for capture resolution which decides at what resolution the frames are captured and sent to the inference pipeline and other is the output resolution which decides at what resolution the output display window should be displayed. 
    - so to have a fair benchmarking we should set the input image resolution same as it directly affects the performance. 
    - the average FPS observed here is around 2.53. 

### Expected FPS as per official benchmarks

- unlike HAILO, we dont have officially noted benchmarks for all model formats on raspberry pi 5 cpu as it is not meaningful to do this for every other cpu out there and moreover when it comes to cpu the performance depends on a lot of other factors such as background processes, memory allocation, etc. 
- still we have some numbers noted by ultralytics specifically for raspberry pi 5 on yolo11n https://docs.ultralytics.com/guides/raspberry-pi/ . But this is only for ONNX format and here also the benchmark is run on `coco.yaml` which is a very large dataset and it will take a long time to run the benchmark. 
- we can instead run benchmark on `coco128.yaml` and get similar results. 

- so we obtained results by running official benchmark command: `yolo benchmark model=yolo11n.pt data=coco128.yaml imgsz=640 device=cpu` which is present on the website https://docs.ultralytics.com/modes/benchmark/
- this isolates model inference speed only removing camera overhead. 
- what this command does is, load the model, export it to different formats, run inference tests, measure inference latency, FPS, Model size, mAP accuracy and finally print a comparison table across runtimes. 
- here we can see that for pytorch, the raw inference speed is around 2.4 FPS and the speed obtained in our experiments is also around 2.53 FPS. 
- So from this we can conclude that at least for inference of PyTorch yolo11n model on Raspberry Pi 5 CPU, the camera is not the bottleneck but the processing power and code optimization is the ultimate bottleneck. That means here we can look at the software optimization part and there is not much that we can do at the hardware optimization side. 

Benchmarks complete for /home/sameer/Desktop/optimization_of_ai_models/AIML_models/computer_vision/detection/yolo11/yolo11n.pt on coco128.yaml at imgsz=640 (330.89s)
Benchmarks legend:  - ✅ Success  - ❎ Export passed but validation failed  - ❌️ Export failed
+----------------------------------------------------------------------------------------------------------+
|      Format                  Status❔   Size (MB)   metrics/mAP50-95(B)   Inference time (ms/im)   FPS   |
+==========================================================================================================+
| 1    PyTorch                 ✅         5.4         0.5099                417.31                   2.4   |
| 2    TorchScript             ✅         10.5        0.5075                472.13                   2.12  |
| 3    ONNX                    ✅         10.2        0.5076                228.33                   4.38  |
| 4    OpenVINO                ✅         10.4        0.506                 92.82                    10.77 |
| 5    TensorRT                ❌         0.0         -                     -                        -     |
| 6    CoreML                  ❌         0.0         -                     -                        -     |
| 7    TensorFlow SavedModel   ❌         0.0         -                     -                        -     |
| 8    TensorFlow GraphDef     ❌         0.0         -                     -                        -     |
| 9    TensorFlow Lite         ❌         0.0         -                     -                        -     |
| 10   TensorFlow Edge TPU     ❌         0.0         -                     -                        -     |
| 11   TensorFlow.js           ❌         0.0         -                     -                        -     |
| 12   PaddlePaddle            ❌         0.0         -                     -                        -     |
| 13   MNN                     ✅         10.1        0.5049                110.88                   9.02  |
| 14   NCNN                    ✅         10.2        0.5041                166.14                   6.02  |
| 15   IMX                     ❌         0.0         -                     -                        -     |
| 16   RKNN                    ❌         0.0         -                     -                        -     |
| 17   ExecuTorch              ✅         10.2        0.5075                214.27                   4.67  |
| 18   Axelera                 ❌         0.0         -                     -                        -     |
+----------------------------------------------------------------------------------------------------------+