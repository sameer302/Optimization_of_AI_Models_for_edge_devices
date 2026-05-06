1) Here we are running benchmark code on hailo NPU using `hailortcli benchmark <hef_path>` command.
2) It is concerned just with the NPU interaction section of a vision model inferencce pipeline.
3) For each benchmark it measures three things, pure hardware fps (no pre and post processing), streaming fps (pre and post processing after running inference included) and hardware latency.
4) Here we have three variables to control viz., power mode of NPU (performance and ultra performance), PCIe generation (Gen2 vs Gen3) and Batch size of input.
5) We will run two classes of experiments here, 
    1) One will be to observe the highest FPS possible for different combinations of the above three variables. This experiment will run for a short duration of time. 
    
    2) The other experiment will be to monitor the temperature of NPU during benchmark inference and for this we will have one batch size (the one corresponding to which we get the highest FPS in the first sub experiment), but we will try for different PCIe generations and different power modes. This experiment will run for a longer duration as we want to see the sustained behaviour of temperature.  

6) Explain the observations made here by referring to the concept of context.