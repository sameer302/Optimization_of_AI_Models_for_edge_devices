1) CPU state

- Here first we need to understand how the CPU state / processing state is related to the AIML inference. So broadly this can be divided into two scenarios, one is when we run the inference on CPU and second when we run the inference on NPU. 

    Case 1) Inference on CPU:-
    - here the frameworks that we use to run AIML inference on CPU such as PyTorch, TensorFlow, OpenCV, etc try to parallelize work using: Threads, Vector instructions, CPU cores. 
    - CPU's have few powerful cores and each core can execute one thread at a time.Each thread runs on a CPU core and inside the core the computation uses vector units. So the number of threads is limited by the number of cores while the rest wait in the scheduler queue.  
    - So the number of threads/cores that are running the inference at a given time will directly influence the inference speed that we get. Hence we need to fix the number of cores/threads that are running to execute the inference and keep this setting common across all experients so that we get comparable results. 

    Case 2) Inference on NPU:-
    - here the framework compiles the model into operations that run on the NPU hardware and parallelism happens through MAC units, Tensor compute arrays, dataflow pipelines. 
    - NPU's don't have cores as CPU but they have multiple small compute units which are specialized hardware for tensor operations. These units work in parallel and execute operations like convolutions, matrix multiplications, activation functions, etc. 
    - Here we dont use threads but the compiler maps tensor operations to many MAC units. So we don't need to control anything here as far as it is concerned with HAILO NPU, it is already set to work at its max capacity so if we are able to provide it data at sufficient speed then it will work at its best. but even here, CPU is used for pre and post processing of data so anyways in the inference pipeline cpu does have a role and so we need to decide the cores and threads that we are going to use from cpu so that we can be sure that any other device that we are benchmarking should have same cpu support. 

- So now coming back to CPU state, we need to fix the number of cores that are being used and if possible also isolate these cores so that other processes don't interfere and we get a clean baseline state. So for this we can check our code/program and see how many threads is it divided into or maybe run the code and when it turns into a process then at real time we can see how many threads does it have and how many are running at any instance of time. 

- Now to know how many threads will my program will break into while running, there are two ways
    1) one way is we look at the code and if the coder has done explicit multithreading then we can tell easily how many threads will this code break into.
    2) another way is we run the program and then at real time see how many threads did this program break into and how many are running at this instance of time. Lets see how to do this first and then we will see why this happens,
        1) Open the process console for e.g. in Linux terminal, run the command, `top` or `htop` (both are similar just htop is more interactive than top)
        2) here we can change the settings by pressing `F2` and the setting to be changed is to toggle, `Tree view` and `Show custom thread names`. these settings will remain in effect only for that particular terminal session.
        3) after this we search for the name of the program for which we want to look the number of threads. so we press `F4` which will open Filter option and then we type the name of the program that we are running for e.g. we type `yolo` and then we are able to see many processes with different id's. 



    1) check cpu governor
        for one core:-
        `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor`
        for all cores:-
        `cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`
        here we get output as ondemand or performance
