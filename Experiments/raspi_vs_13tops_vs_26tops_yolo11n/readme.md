## AIM: To compare the performance of Vision model inference on raspberry pi 5 CPU Only, CPU + 13 TOPS NPU and CPU + 26 TOPS NPU.

### Hardware specifications:

1) Raspberry PI 5 SBC
2) HAILO 8L board with 13 TOPS NPU
3) HAILO 8 board with 26 TOPS NPU
4) 5 MP ov5647 Camera module

### Software specifications:

1) Vision model:- YOLO11n
2) Inference framework:- ultralytics, ncnn, hailort

### Sub experiment 1:
Verifying TOPS for AI HAT+

## Post-experiment analysis

### Observation 1 : Camera as bottleneck

- The first bottleneck that may arise in the inference pipeline is the rate at which frames are being captured and sent to the CPU by the camera.

- For the camera that we are using, ov5647, rate of capturing frame depends on the input resolution that we want. The exact details are, 

    Available cameras  
    0 : ov5647 [2592x1944 10-bit GBRG] (/base/axi/pcie@1000120000/rp1/i2c@80000/ov5647@36)
        Modes: 'SGBRG10_CSI2P' : 640x480 [58.92 fps - (16, 0)/2560x1920 crop]
                                1296x972 [46.34 fps - (0, 0)/2592x1944 crop]
                                1920x1080 [32.81 fps - (348, 434)/1928x1080 crop]
                                2592x1944 [15.63 fps - (0, 0)/2592x1944 crop]

- what happens here is that we decide the exact input resolution and then the camera selects the sensor mode matching that resolution or if we choose any arbitray resolution then the camera matches it with nearest sensor mode, captures the frame and then scales it to the desired resolution. Now each sensor mode has a fixed maximum FPS. Hence resolution directly determines max FPS. 

- there are following levels at which fps speed will differ, 
    1) hardware or sensor speed (fastest)
    2) capture speed or the speed at which our python code recieves these frames
    3) recording speed, capturing + storing 
    4) displaying speed, capturing + displaying 
    5) recording + displaying speed 
    6) inference + record
    7) inference + display
    9) inference + record + display (slowest)

- initially, by default the configuration of camera is such that the sensor speed at each input resolution is pre-fixed. To understand this we need to know about some parameters related to camera which determine the sensor speed and image quality

    1) ExposureTime (Shutter Time) : 
        - how long the sensor collects light for each frame. 
        - unit is microseconds. 
        - increasing exposure results in brighter image, more light captured, more motion blur (rolling shutter effect). 
        - decreasing exposure results in darker image, less light captured, less blur.
        - by default AeEnable parameter is set to True and so it adjusts its value according to surrounding lighting. 
        - but this adjustment is by default slow and it also affects the FrameDuration as ExposureTime <= FrameDuration.
        - range of values allowed for ExposureTime as, (min, max, default) at different resolutions can be found out by running the `camera_default.py` script. This will print the current parameter values and also the default values. After running this script we can see the output as 



        Available Sensor Modes:

        0: Resolution = (640, 480) | Max FPS ≈ 58.92
        1: Resolution = (1296, 972) | Max FPS ≈ 46.34
        2: Resolution = (1920, 1080) | Max FPS ≈ 32.81
        3: Resolution = (2592, 1944) | Max FPS ≈ 15.63



        Selected Mode: (640, 480)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 33167
        FrameDuration (µs): 33302

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (134, 4879289, 20000)
        FrameDurationLimits: (16971, 4879899, (33333, 33333))




        Selected Mode: (1296, 972)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 33239
        FrameDuration (µs): 33326

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (86, 3066985, 20000)
        FrameDurationLimits: (21581, 3067365, (33333, 33333))
        




        Selected Mode: (1920, 1080)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 33216
        FrameDuration (µs): 33326

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (110, 3066979, 20000)
        FrameDurationLimits: (30483, 3067365, (33333, 33333))





        Selected Mode: (2592, 1944)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 63835
        FrameDuration (µs): 63965

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (130, 3066985, 20000)
        FrameDurationLimits: (63965, 3067365, (33333, 33333))




        - here firstly we can see that the default value of AeEnable is True, also the runtime value of ExposureTime is 33216 microseconds which is different from the default value of 20000 (except the last case). This is because the default value of FrameDuration is ~33 microsec (~30 fps) and so Ae tries to use full frame time for light collection. 
        - if we keep the Ae set to true but remove the constraint from FrameDurationLimits and set it to its natural overall range i.e., (16971, 3067365) then we get the results as, 



        Selected Mode: (640, 480)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 66638
        FrameDuration (µs): 66773

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (134, 4879289, 20000)
        FrameDurationLimits: (16971, 4879899, (33333, 33333))




        Selected Mode: (1296, 972)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 66652
        FrameDuration (µs): 66739

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (86, 3066985, 20000)
        FrameDurationLimits: (21581, 3067365, (33333, 33333))




        Selected Mode: (1920, 1080)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 66653
        FrameDuration (µs): 66764

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (110, 3066979, 20000)
        FrameDurationLimits: (30483, 3067365, (33333, 33333))




        Selected Mode: (2592, 1944)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 66663
        FrameDuration (µs): 66793

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (130, 3066985, 20000)
        FrameDurationLimits: (63965, 3067365, (33333, 33333))



        - initially as there was constraint on the FrameDurationLimits due to which FrameDuration was restricted to ~33 microsec, hence even though Ae was set to true it was not able to increase ExposureTime beyond 33 microsec, but now when we removed the constraint from FrameDuration, Ae showed it's effect and it chose a high value of ~ 66 microsec and accordingly FrameDuration also adjusts it's time to match the relation ExposureTime <= FrameDuration. 
        - So ideally this is the best case scenario where camera tries to capture the best bright image which will eventually help in better inference but this comes at a cost of reduced fps. But this is not a universal problem, for the same quality of bright image we may have other cameras which require less exposure time and eventually give better fps. The relation here is, Light ∝ ExposureTime x Sensitivity. So in order to achieve better light with less exposure time we need to use lens with better sensitivity . 

        - Now in next case, we set AeEnable to False while let the constraints on FrameDuration be as it is, lets see what we get in this case, 



        Selected Mode: (640, 480)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 976
        FrameDuration (µs): 33302

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (134, 4879289, 20000)
        FrameDurationLimits: (16971, 4879899, (33333, 33333))




        Selected Mode: (1296, 972)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 996
        FrameDuration (µs): 33326

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (86, 3066985, 20000)
        FrameDurationLimits: (21581, 3067365, (33333, 33333))



        Selected Mode: (1920, 1080)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 994
        FrameDuration (µs): 33326

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (110, 3066979, 20000)
        FrameDurationLimits: (30483, 3067365, (33333, 33333))        



        Selected Mode: (2592, 1944)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 975
        FrameDuration (µs): 63965

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (130, 3066985, 20000)
        FrameDurationLimits: (63965, 3067365, (33333, 33333))



        - here ExposureTime resets to a default safe minimum which depends on sensor timing granularity, line time, pixel clock, sensor hardware constraints, etc. 
        - Next lets set AeEnable to False and also remove the constraint from FrameDurationLImits. After this we get the results as, 



        Selected Mode: (640, 480)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 976
        FrameDuration (µs): 16971

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (134, 4879289, 20000)
        FrameDurationLimits: (16971, 4879899, (33333, 33333))        



        Selected Mode: (1296, 972)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 996
        FrameDuration (µs): 21581

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (86, 3066985, 20000)
        FrameDurationLimits: (21581, 3067365, (33333, 33333))



        Selected Mode: (1920, 1080)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 994
        FrameDuration (µs): 30483

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (110, 3066979, 20000)
        FrameDurationLimits: (30483, 3067365, (33333, 33333))



        Selected Mode: (2592, 1944)

        --- Current Runtime Values (Metadata) ---
        ExposureTime (µs): 975
        FrameDuration (µs): 63965

        --- Supported Control Ranges (min, max, default) ---
        AeEnable: (False, True, True)
        ExposureTime: (130, 3066985, 20000)
        FrameDurationLimits: (63965, 3067365, (33333, 33333))



        - In this case we can see that as we turned off Ae hence ExposureTime chose the default safe minimum and as we removed the constraints from FrameDuration, it also chose the minimum value that was allowed in the range in order to increase the fps. So in this particular scenario we will get the highest possible fps for each input resolution, i.e. when AeEnable is turned off and we remove the constraints from FrameDuration. To put it in other words we can say that whenever given freedom, FrameDuration tries to achieve the least allowed value and increase the fps, ExposureTime tries to increase its value and reduce fps and if both are free then ExposureTime wins over FrameDuration. 

        - So by turning AeEnable off and setting appropriate value of FrameDuration, we can get any desired value of sensor fps (in the allowed range of FrameDuration). 

        - Now the question arises is that should we manually set the value of FrameDuration or let the Ae decide its value or should we go with the default value of ~33 microsec which gives us a speed of ~30 fps.

        - So as of now, let the setting be as it is to the default value and lets look at the drop of fps at each higher level. Then if in any case we see that the final inference is directly related to the initial sensor fps then we will increase this value in order to check the exact bottleneck. 

    2) FrameDurationLimits
        - total time allocated for one frame.
        - FPS = 1 / FrameDuration
        - so if AeEnable is set to True then Ae will adjust the ExposureTime to capture maximum light and if FrameDurationLimits is set to default then it is default FrameDuration value (~33 microsec) which drives the ExposureTime value (as it tries to utilize nearly complete FrameDuration to capture light) and also the FPS value.
        - but if AeEnable is set to True and we remove the constraints from FrameDurationLimits and let it move around its default min and max range, then it is the ExposureTime which drives the FrameDuration value which eventually drives the FPS speed that we achieve. 

        |---- ExposureTime ----|---- Remaining idle/readout time ----|
        <--------------------- FrameDuration ------------------------>

        - ExposureTime controls brightness and motion blur while FrameDuration controls FPS. When Ae is active then FrameDuration ~ ExposureTime because Ae tries to use full frame time for light collection. 
        - By controlling the value of FrameDuration we can also the control the value of FPS that can be obtained and hence effectively we can supply frames at any FPS (in the allowed range) to the CPU for processing. 

- So now firstly by modifying the values of ExposureTime and FrameDuration, we can control the rate at which frames will be captured at the lowest level or closest to the hardware or sensor. This is necessary because if we want to find out other bottlenecks in our inference pipeline we should make sure that camera is working at its max speed but if increasing fps speed from camera does not benifit in increasing fps then it means the bottleneck is present in the further pipeline.

- In the yolo11n_cpu.py script, we are not controlling the rate at which we want to send frames to our CPU but we are controlling the input resolution which indirectly controls the rate at which camera will capture and send frames. 

- So I need to check if camera is the bottleneck. For this firstly I should compare sensor level fps, then capture fps i.e. fps at which python captures those frames, then record fps, then record + display fps and then inference fps so that we can clearly see at each step how muuch latency is being added.  