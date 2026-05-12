1) CPU cores state

- Here first we need to understand how the CPU state / processing state is related to the AIML inference. So broadly this can be divided into two scenarios, one is when we run the inference on CPU and second when we run the inference on NPU. 

    Case 1) Inference on CPU:-

    - here the frameworks that we use to run AIML inference on CPU such as TFlite, PyTorch, OpenCV, NumPy, MKL, OpenMP etc try to parallelize work using: Threads, Vector instructions, CPU cores. 

    - CPU's have few powerful cores and each core can execute one thread at a time.Each thread runs on a CPU core and inside the core the computation uses vector units. So the number of threads is limited by the number of cores while the rest wait in the scheduler queue. OS scheduler keeps context switching the threads which results in unstable latency. 

    - So the number of threads/cores that are running the inference at a given time will directly influence the inference speed that we get. Hence we need to fix the number of cores/threads that are running to execute the inference and keep this setting common across all experiments so that we get comparable results. 


    Case 2) Inference on NPU:-

    - here the framework compiles the model into operations that run on the NPU hardware and parallelism happens through MAC units, Tensor compute arrays, dataflow pipelines. 

    - NPU's don't have cores as CPU but they have multiple small compute units which are specialized hardware for tensor operations. These units work in parallel and execute operations like convolutions, matrix multiplications, activation functions, etc. 

    - Here we dont use threads but the compiler maps tensor operations to many MAC units. So we don't need to control anything here as far as it is concerned with HAILO NPU, it is already set to work at its max capacity so if we are able to provide it data at sufficient speed then it will work at its best. but even here, CPU is used for pre and post processing of data so anyways in the inference pipeline cpu does have a role and so we need to decide the cores and threads that we are going to use from cpu so that we can be sure that any other device that we are benchmarking should have same cpu support. 


- So now coming back to CPU state, we need to fix the number of cores that are being used and if possible also isolate these cores so that other processes don't interfere and we get a clean baseline state.

- Now to know how many threads will my program break into while running, there are two ways

    1) one way is we look at the code and if the coder has done explicit multithreading then we can tell easily how many threads will this code break into.

    2) another way is we run the program and then at real time see how many threads did this program break into and how many are running at this instance of time. Lets see how to do this first and then we will see why this happens,

        1) Open the process console for e.g. in Linux terminal, run the command, `top` or `htop` (both are similar just htop is more interactive than top)

        2) here we can change the settings by pressing `F2` and the setting to be changed is to toggle, `Tree view` and `Show custom thread names`. these settings will remain in effect only for that particular terminal session.

        3) after this we search for the name of the program for which we want to look the number of threads. so we press `F4` which will open Filter option and then we type the name of the program that we are running for e.g. we type `yolo` and then we are able to see many processes with different id's. 

        4) This view shows us different processes / threads running under the name yolo. Also in our case we are running a script which internally runs two programs so our main script acts like a parent process here and the two programs that it runs acts like child processes. And then for each such child process, the process itself is a thread (main thread) as it is what breaks the program further into many smaller threads. This is the structure that we can see on the screen for the particular above scenario. 

        5) From this display itself by just counting we can tell that the number of threads for our yolo11n inference program is 20. And also if we observe carefully then the value of column S(status) tells us the status of the process/thread i.e. whether it is running (R) or sleeping (S). So even this window has mostly all what we need but still we can use one more terminal window which will give us more insight in simplified view. 

        6) For this we look at the process/child process corresponding to our program and note its process id (PID). Then in another terminal window we can run the command, `top -H -p <PID>`. This will give us a metadata at the top like, 

        Threads:  20 total,   1 running,  19 sleeping,   0 stopped,   0 zombie
        %Cpu(s): 58.7 us,  6.4 sy,  0.0 ni, 34.9 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st 
        MiB Mem :  16214.9 total,  10765.7 free,   3535.6 used,   2328.4 buff/cache     
        MiB Swap:   2048.0 total,   2048.0 free,      0.0 used.  12679.3 avail Mem 

        From the above metadata related to our process we get to know a lot of info. and most importantly I can observe that the number of threads of this particular program running is fluctuating, at once it is running on single core (single thread) and next instance its running on 3 cores (3 threads), hence it is necessary to clamp the number of cores being used and isolate them and then conduct the experiments so that the results are not affected due to randomness in execution. One point to note here is that in this display, the running threads are shown in bold while others are normal font but then we can see that some normal font threads also show %CPU but the reason behind this is that the %CPU reading is averaged a short time interval so if that thread was running in near past then it might show some %CPU reading even when currently its not running on CPU. 

        7) Now before clamping the number of cores, I should know how is the thread to core assignment being handled by default so that I know in real time which condition to use. So by default, threads from different programs often run on the same core and the scheduler continuously adjusts based on system load. One core picks a thread randomly from the queue, runs it for a short duration of time and then picks another thread. On the other hand, one thread runs on one core for a short interval, then on another core and it keeps hopping in this way. 

        8) When we isolate cores and bind processes to it, then the scheduler will not assign any other process to these cores. But even then, threads of that particular process will be assigned to these cores in time slices so threads will time share the isolated cores. If threads > cores, they time slice, if threads <= cores, they run simultaneously but migrate from one core to other as per normal Linux scheduler rules. We can also pin threads to exact cores if we want. 

- Now lets see how to set this baseline. 

    1) First of all we will limit the number of threads that our inference program breaks into so that we can be sure that the inference operation happens all at once on the number of cores that are being allotted to it. A simple example to understad this is that, lets say we have to perform the matrix multiplication, 
    C = A x B, without restriction the framework splits this into many chunks, 
    thread1 -> rows 1-50, thread2 -> rows 51-100, thread3 -> 101-150, thread4 -> 151-200, but if we restrict the program to just break into two threads then, thread1 -> rows 1-100 and thread2 -> rows 101-200. So the algorithm stays same only number of parallel workers changes. So we need to use the code as used below in order to restrict our code,

    ```
    import os

    NUM_THREADS = 3 

    os.environ["OMP_NUM_THREADS"] = str(NUM_THREADS)
    os.environ["OPENBLAS_NUM_THREADS"] = str(NUM_THREADS)
    os.environ["MKL_NUM_THREADS"] = str(NUM_THREADS)
    os.environ["NUMEXPR_NUM_THREADS"] = str(NUM_THREADS)

    import torch
    torch.set_num_threads(NUM_THREADS)
    torch.set_num_interop_threads(1)

    import sys
    import argparse
    import glob
    import time
    import csv

    import cv2
    cv2.setNumThreads(NUM_THREADS)

    import numpy as np
    from ultralytics import YOLO
    from datetime import datetime
    ```

    In the above code we are restricting certain system level libraries to break into the number of threads specified by us. Most of these libraies, if left free will break into number of threads corresponding to the number of available cores (overall 20 by default) but when we set the number of threads to be 3, the number of threads reduces to 18.
    Similarly if we set the number of threads to 4 or higher then we will see that the total number of threads that our program breaks into will increase (22/21 from 20). This is because, total threads = base threads + sum (each library's thread pool)
    
    So we saw that the system level libraries tend to break into number of threads so that true parallelism should be achieved which is possible only when number of threads = logical computing units (number of cores). Then why do we see the total number of threads for our inference program being upto 20 ? This is because the extra threads come from other components such as, Camera (OpenCV / Picamera), GUI, Python runtime, Pytorch backend, etc. Total threads is the sum of all thread pools. 
    
    So if we want more granular control on processing then we can try to remove sources of extra threads for e.g. disable GUI. But still we can't bring the entire pipeline to work in just 3/4 threads as the runtime itself needs more threads. 
    
    In the above code, minimum we can set number of threads = 1 and maximum = 4 (max number of logical cores), we can set more number of threads > 4 also but then they will time share the cores and it might even reduce performance due to excessive context switching. Now lets set our CPU to assign cores to our code. 

    2) By using the command, `taskset -c 0,1 python inference.py` we can restrict the process to specific CPU cores. But this does not restrict the scheduler from assigning other processes to these cores hence we need to one more step in order to isolate the cores. 

    3) In order to isolate these cores, we need to use the following command, 
    `sudo nano /boot/firmware/cmdline.txt`
    here we will be able to see a long text line, at the end of this line I need to append, `isolcpus = 2,3` where on RHS we can give any number of cores which we want to isolate. After this we need to make sure to reboot our system or else the isolation wont work


    1) check cpu governor
        for one core:-
        `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor`
        for all cores:-
        `cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`
        here we get output as ondemand or performance
