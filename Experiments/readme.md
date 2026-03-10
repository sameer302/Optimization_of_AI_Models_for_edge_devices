## rationale behind noting each of the system metric

1) core voltage (get_voltage function):-
In both thermal throttling and undervoltage (power) throttling, the Raspberry Pi reduces the CPU frequency first. Due to Dynamic Voltage and Frequency Scaling (DVFS), a lower frequency allows the system to operate at a lower core voltage, so the voltage decreases afterward. In thermal throttling the trigger is high temperature, while in power throttling the trigger is low supply voltage, but in both cases the frequency reduction leads to reduced voltage and lower power consumption. The formula goes like P ∝ V^2 × f
