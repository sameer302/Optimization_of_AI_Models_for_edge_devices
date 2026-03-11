1) CPU state
    1) check cpu governor
        for one core:-
        `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor`
        for all cores:-
        `cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`
        here we get output as ondemand or performance
