1) Stands for Peripheral Component Interconnect Express.

2) Raspberry Pi 5 has an Flexible Printed Circuit (FPC) connector which provides a PCIe Gen 2.0 x1 interface (by default) for fast peripherals.

3) If we connect HAT+ device via PCIe then it is automatically detected and PCIe gen 2.0 interface starts working but if we want to connect a non-HAT+ device we should connect it to Raspberry Pi and then manually enable PCIe.

4) Raspberry Pi 5 is not certified for Gen 3.0 speeds but to enable PCIe gen 3.0 we need to do the following changes :
    a) by default Gen 2.0 is used with speed 5 GT/s.
    b) to use Gen 3.0 (8 GT/s), we need to add following line to `/boot/firmware/config.txt` : dtparam=pciex1_gen=3
    c) reboot the system after making above changes

5) We can also boot raspberry pi 5 device from PCIe storage (NVMe SSD). For this we need to change the `BOOT_ORDER` in the bootloader configuration. Edit the EEPROM configuration with the following command: `sudo rpi-eeprom-config --edit`, Replace the BOOT_ORDER line with the following line: `BOOT_ORDER=0xf416`. To boot from a non-HAT+ device, also add the following line: `PCIE_PROBE=1`. After this reboot Raspberry Pi 5 using `sudo reboot`

6) Transfer speed of PCIe interfaces:

What does GT/s mean?

GT/s = GigaTransfers per second

It counts symbol transfers, not bytes
PCIe uses serial signaling, so each “transfer” is a group of bits

Step-by-step: 8 GT/s → ~1 GB/s

1️) Raw signaling rate (PCIe Gen 3)

PCIe Gen 3 = 8 GT/s
Each transfer carries 1 bit per lane per symbol
Raw bit rate: 8 × 10⁹ bits/s

2️) Encoding overhead (very important)

PCIe Gen 3 uses 128b/130b encoding
(This replaced 8b/10b used in Gen 1/2)

For every 130 bits transmitted Only 128 bits are actual data
Efficiency = 128 / 130 ≈ 98.46%

So effective data rate: 8 × 10⁹ × (128/130) ≈ 7.877 × 10⁹ bits/s

3️) Convert bits → bytes

There are 8 bits = 1 byte

7.877 × 10⁹ ÷ 8 ≈ 0.985 × 10⁹ bytes/s

Final result

PCIe Gen 3 ×1 (8 GT/s) ≈ 985 MB/s ≈ ~1 GB/s (theoretical maximum)

For comparison (useful context)

| PCIe Gen  | Encoding      | GT/s       | Bandwidth per lane |
| --------- | ------------- | ---------- | ------------------ |
| Gen 2     | 8b/10b        | 5 GT/s     | ~500 MB/s          |
| Gen 3     | 128b/130b     | 8 GT/s     | ~985 MB/s          |
| Gen 4     | 128b/130b     | 16 GT/s    | ~1.97 GB/s         |
