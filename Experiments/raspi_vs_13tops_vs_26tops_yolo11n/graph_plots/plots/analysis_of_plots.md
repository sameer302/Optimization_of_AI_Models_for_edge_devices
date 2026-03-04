1) temperature_vs_time:-
    - https://www.raspberrypi.com/documentation/computers/config_txt.html#raspberry-pi-4:~:text=Monitoring%20core%20temperature 
    - When the core temperature is between 80°C and 85°C, the Arm cores will be throttled back. If the temperature exceeds 85°C, the Arm cores and the GPU will be throttled back.
    - For the Raspberry Pi 3 Model B+, when the soft limit is reached, the clock speed is reduced from 1.4 GHz to 1.2 GHz, and the operating voltage is reduced slightly. This reduces the rate of temperature increase: we trade a short period at 1.4 GHz for a longer period at 1.2 GHz. By default, the soft limit is 60°C. This can be changed via the temp_soft_limit setting in config.txt.
    - For Raspberry Pi 5, the exact temperature for soft limit and hard limit is not specifically mentioned but it can be found out experimentally by running some stress code  such as `stress-ng --cpu 4 --timeout 600` 
    - Due to this we can see that the temperature gets settled around 60 degree celsius, cpu frequency stayed constant at it's maximum capacity of 2.4 GHz and no throttling flags were shown.
    
2) cpu_frequency_vs_time:-
    - as per product sheet raspberry pi 5 has BCM2712 processor which operates at 2.4GHz frequency normally and this frequency will be reduced in case of thermal throttling. 
    - but as in our case there was nor thermal throttling hence the cpu frequency stayed constant. 

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

6) throttle_flags_vs_time:-
    - this is a firmware utility provided by the Raspberry Pi firmware, not directly by the OS or by user software. 
    - here we can see that no throttle flag was set during the entire inference timeline. 
    - This indicates there was no event of throttling neither due to thermal throttling nor due to power throttling. 
    - Throttling status can be understood by looking at the flags index given on the official website https://www.raspberrypi.com/documentation/computers/os.html#get_throttled  
    - We didnt see any throttle flags which means that the soft limit is well above 60 degree celsius. 