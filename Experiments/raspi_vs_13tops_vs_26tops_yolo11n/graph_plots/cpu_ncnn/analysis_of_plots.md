## Running yolo11n ncnn model inference on CPU

- Here we are deciding the input resolution at which camera captures frames and also the resolution at which model runs its inference, by giving the argument `--capture-resolution`
- Here the batch size is implicitly set to 1 in the code and it makes sense because for live camera feed if we set batch size larger than 1 then we need to accumulate frames which will lead to latency. 

1) temperature_vs_time:-
    - Here we can see that the temperature gets settled around 65 degree celsius, cpu frequency stayed constant at it's maximum capacity of 2.4 GHz and no throttling flags were shown.
    - This temperature reading is quite more than what we observed while running pytorch model. 
    
2) cpu_frequency_vs_time:-
    - as in our case there was no thermal throttling hence the cpu frequency stayed constant. 

3) cpu_percentage_vs_time:-
    - here we can see that our code is using nearly 80% of CPU and whatever results we are observing are just with this 80% utilization. Also this is not just the utilization by our program but overall utilization which includes OS and other processes also utilizing CPU
    - just like temperature the cpu utilization here is more as compared to pytorch framework.

4) memory_percentage_vs_time:-
    - here we can see that our program used nearly 15-16% of RAM and this is not just used by our program but it's overall usage so it includes OS and other processes utilization also. 
    - here we are getting a benifit as the memory utilization of ncnn format is less as compared to pytorch. 


5) cpu_voltage_vs_time:- 
    - here the voltage we are measuring is the voltage drawn by CPU core. The voltage drawn by board is different and then each component internally has their own share of voltage to operate on.
    - CPU voltage drawn stayed constant here indicating that there was no event of thermal or power throttling 

6) throttle_flags_vs_time:-
    - We didnt see any throttle flags which means that the soft limit is well above 60 degree celsius. 

7) fps_vs_time:-
    - the average fps observed here is around 7.12 FPS which is much better than what was observed for pytorch framework. 

### Expected FPS as per official benchmarks

- unlike HAILO, we dont have officially noted benchmarks for all model formats on raspberry pi 5 cpu as it is not meaningful to do this for every other cpu out there and moreover when it comes to cpu the performance depends on a lot of other factors such as background processes, memory allocation, etc. 
- still we have some numbers noted by ultralytics specifically for raspberry pi 5 on yolo11n https://docs.ultralytics.com/guides/raspberry-pi/ . But this is only for ONNX format and here also the benchmark is run on `coco.yaml` which is a very large dataset and it will take a long time to run the benchmark. 
- we can instead run benchmark on `coco128.yaml` and get similar results. 

- so we obtained results by running official benchmark command: `yolo benchmark model=yolo11n.pt data=coco128.yaml imgsz=640 device=cpu` which is present on the website https://docs.ultralytics.com/modes/benchmark/
- this isolates model inference speed only removing camera overhead. 
- what this command does is, load the model, export it to different formats, run inference tests, measure inference latency, FPS, Model size, mAP accuracy and finally print a comparison table across runtimes. 
- here we can see that for ncnn, the raw inference speed is around 6.02 FPS and the speed obtained in our experiments is around 7.12 FPS. 
- So from this we can conclude that even for inference of ncnn yolo11n model on Raspberry Pi 5 CPU, the camera is not the bottleneck but the processing power and code optimization is the ultimate bottleneck. That means here we can look at the software optimization part and there is not much that we can do at the hardware optimization side. 

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