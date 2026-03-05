## Running yolo11n hef model inference on HAILO 8 (26 TOPS)

- When we convert model to HEF using HAILO DFC, it happens at a fixed input resolution and if we want to change that input resolution then we need to recompile our model again using the compiler.
- To know at what input resolution a particular model was converted to HEF we can use the command `hailortcli parse-hef your_model.hef`
- Same happens with some other model formats also, some are flexible for input resolution and can be decided at runtime while others are fixed. 
- So here when we run the benchmark command `hailortcli benchmark your_model.hef` we don't need to give input resolution argument as it is already hardcoded during compilation. 
- similalrly when we run the model using 
- Summary
=======
FPS     (hw_only)                 = 104.908
        (streaming)               = 104.909
Latency (hw)                      = 7.75396 ms

- These benchmark values are different from what is mentioned on the official HAILO MODEL ZOO github repo (185 fps for batch size = 1, yolo11n)

- Finally even the values given on the official HAILO MODEL ZOO do not indicate towards 26 TOPS speed but a speed significantly lower than that. 
- 26 TOPS is theoretical peak capacity under ideal/synthetic conditions, not real-world performance.
- FPS × GFLOPs gives effective TOPS, which is always lower due to memory bottlenecks, idle cycles, and layer transitions.
- GFLOPs in model zoos only count MAC operations, undercounting total operations the chip actually performs.
- After Hailo compiler optimization, the model changes — original GFLOPs no longer map 1:1 to hardware ops.
- This is industry-wide practice — Google, Intel, Qualcomm all market peak theoretical TOPS the same way.
- TOPS = hardware ceiling. FPS × GFLOPs = actual utilization. Both are true, just measuring different things.