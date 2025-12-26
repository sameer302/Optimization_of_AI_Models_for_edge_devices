Stands for Peripheral Component Interconnect Express.

Raspberry Pi 5 has an Flexible Printed Circuit (FPC) connector which provides a PCIe Gen 2.0 x1 interface (by default) for fast peripherals.

If we connect HAT+ device via PCIe then it is automatically detected and PCIe gen 2.0 interface starts working but if we want to connect a non-HAT+ device we should connect it to Raspberry Pi and then manually enable PCIe.

Raspberry Pi 5 is not certified for Gen 3.0 speeds but to enable PCIe gen 3.0 we need to do the following changes :
    a) by default Gen 2.0 is used with speed 5 GT/s.
    b) to use Gen 3.0 (8 GT/s), we need to add following line to `/boot/firmware/config.txt` : dtparam=pciex1_gen=3
    c) reboot the system after making above changes

We can also boot raspberry pi 5 device from PCIe storage (NVMe SSD). For this we need to change the `BOOT_ORDER` in the bootloader configuration. Edit the EEPROM configuration with the following command: `sudo rpi-eeprom-config --edit`, Replace the BOOT_ORDER line with the following line: `BOOT_ORDER=0xf416`. To boot from a non-HAT+ device, also add the following line: `PCIE_PROBE=1`. After this reboot Raspberry Pi 5 using `sudo reboot`
