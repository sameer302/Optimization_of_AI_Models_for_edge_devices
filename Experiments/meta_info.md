### General instructions:-
1) execute a program multiple times (multiple trials of the same experiment) and note average values for plotting
2) keep the environment controlled across different tests in the same experiment. 
3) setting up hardware and software environments
4) designing appropriate workloads
5) defining performance metrics
6) choose the current best model supported by the hardware
7) note down the baseline measurements of temperature, SOTA benchmarks, power consumption, etc. 
8) set the timeline for which the experiment is being conducted.
9) log the metrics continuously over a trial (such as temperature, power consumption, FPS, inference time) and then compare the peak or average values, while some metrics will be logged only once for one trial (such as accuracy, precision)
10) Try to find correlation between the metrics and find thresholds for each metric.
11) Find reason for the observations made or the results obtained

### Possible experiments:-

1) Compare the performance when different generation PCIe interface is used to connect AI accelerators. 

2) Compare the difference when input image resolution is changed.

3) Compare the performance of using different inference framework like ONNX, tensorflow lite, hef, etc.

4) Once we have done experiments on complete AI models we can break the experiments into performing each involved tasks (like matrix multiplications / multithreading / processor intensive tasks, data transfer / memory intensive tasks, etc.). Also when we are doing this the performance metrics that we are using will depend on the task that we are performing.

5) Compare the performance with and without cooling mechanisms. 
