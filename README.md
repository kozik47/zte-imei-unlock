# Unlock Code Generation for ZTE ZXIC SZXF ZX297520V3-Based Devices

Two Python scripts are provided to generate unlock codes for devices utilizing the ZTE ZXIC SZXF ZX297520V3 platform, such as the MTN Hisense H220m 4G MiFi router, and to compute the transform map integral to the unlock code algorithm. These scripts were developed through reverse-engineering of the device's firmware which enabled discovery of the network unlock code generation mechanism.

## Hardware Description

The Hisense H220m, a portable 4G LTE MiFi router, is powered by the ZTE ZX297520V3 platform, incorporating an ARMv7 processor and an integrated 4G LTE modem. USB connectivity provides a virtual Ethernet interface and mass storage functionality when a micro-SD card is inserted. The hardware configuration is summarized:

| Component | Description |
| --- | --- |
| **CPU and Modem** | ZTE ZX297520V3, ARMv7 revision 4 processor with integrated LTE modem (150 Mbps downlink, 50 Mbps uplink, 28nm process). |
| **Flash Memory** | Fudan FM25LS01, 1-Gbit SPI SLC NAND flash (128 MiB, WSON8 package) for firmware storage. |
| **Wi-Fi** | Realtek RTL8189ES, 802.11n WLAN with SDIO interface, supporting up to 150 Mbps. |
| **Power Management** | ZXIC ZX234296, power management unit (PMU) for power distribution. |
| **LTE RF** | ZXIC ZX234220A1, LTE radio frequency ASIC for signal processing. |
| **Power Amplifier** | SMMI S5643-51, multi-band LTE power amplifier supporting low, mid, and high bands. |
| **Battery Charger** | ETA40543, 1.2A/16V linear charger for the 2100 mAh Li-ion battery. |
| **USB** | USB OTG controller (integrated in ZX297520V3), supports virtual Ethernet (CDC Ethernet) and mass storage for SD cards. |
| **Other Interfaces** | I2C (zx29_i2c.0, zx29_i2c.1), UART (ttyS1 at 921600 baud), 136 GPIO pins, MMC/SD controllers (zx29_sd.0, zx29_sd.1). |

The ZX297520V3 chipset serves as the primary processing and communication unit, while the Realtek RTL8189ES enables Wi-Fi connectivity. The SMMI S5643-51 amplifies LTE signals, and the ZXIC ZX234220A1 handles radio frequency tasks. Power distribution is managed by the ZXIC ZX234296, with the ETA40543 charging the battery. The USB OTG controller facilitates network and storage interfaces. UART boot logs indicate a 128x128 LCD (although not present on this device) and a Realtek WLAN driver (version 1.7).

## Reverse-Engineering

The unlock code generation algorithm was determined through reverse-engineering of the MTN Hisense H220m firmware as follows:

1. **UART Output Logging**:

   - A USB to TTL adapter, configured at 3.3V and 921600 baud, was used to capture the UART output.
   - The boot log indicated the device was utilizing U-Boot 2011.09 and Linux kernel 3.4.110-rt140 and also provided hardware details, including the ZX297520V3 CPU, 64 MiB RAM, and NAND flash partitions (e.g., 'rootfs' at 22 MiB).
   - A login shell was visible on the console. It appeared that 'admin' was a valid username but the correct password could not be determined. Therefore dumping the flash was necessary to gain access to the filesystem.

2. **NAND Flash Dumping**:

   - The Fudan FM25LS01 NAND flash (WSON8 package) was desoldered.
   - An XGecu T56 programmer was used to read the 128 MiB flash, yielding a firmware dump with partitions such as 'zloader', 'uboot' and 'rootfs'.

3. **Filesystem Extraction**:

   - The NAND dump contained UBIFS images. Out-of-band data, including error correction codes, was removed with a small script.
   - A custom Python script was developed to extract the 'rootfs' UBIFS image, revealing the filesystem with executables and configuration files.
   - The 'rootfs' `/etc/passwd` file contained a single entry `admin:$1$CIFeJAO5$CA0KJBqrSX6ciPKBlKV8J/:0:0:root:/:/bin/sh`. John the Ripper was run over this entry against a few common wordlists but a valid password was not found.

4. **Binary Analysis**:

   - The  `/bin/goahead` binary was analyzed using Ghidra.
   - An function with the signature `undefined FUN_00016d60(char * param_1, size_t param_2)` was identified as the unlock network code generator.

5. **Algorithm Determination**:

   - The algorithm processes the first 15 IMEI digits, mapping each via a transform map, summing eight consecutive transformed digits per position, and computing the modulo 10 result to generate each unlock code digit.
   - Testing with known IMEI:unlock_code pairs demonstrated that two sufficiently different pairs generally suffice to determine the transform map using the Z3 theorem prover.

6. **Script Development**:

   - The `imei_to_unlock_code.py` script was implemented to generate unlock codes using a predefined transform map from the Hisense H220m.
   - The `compute_transform_map.py` script was developed to calculate transform maps for devices employing this algorithm, given sufficient IMEI:unlock_code pairs.

## Algorithm Description

The unlock code (referred to as the 'unlock_network_code' internally) is an 8-digit sequence and is generated from the first 15 digits of the IMEI:

1. Non-digit characters in the IMEI are converted to 0.
2. Each digit is transformed using a map that assigns digits 0–9 to other digits (0–9).
3. For each position i (0 to 7), the sum of the transformed values of digits i to i+7 is computed, and the result modulo 10 yields the i-th unlock code digit.

### Explanation of Dual Transform Maps

Typically, two valid transform maps are identified for a given device. This arises from the algorithm’s structure:

- Consider a valid transform map, referred to as map1.
- A second map, map2, is defined such that each mapped value is increased by 5 modulo 10 (e.g., if map1 maps 0 to 1, map2 maps 0 to 6).
- For a sum of eight transformed digits, map2 increases the sum by 8 \* 5 = 40.
- Since 40 modulo 10 equals 0, both maps produce identical unlock code digits.
- For example, if map1 is {0:1, 1:3, 2:5, 3:7, 4:9, 5:0, 6:2, 7:4, 8:6, 9:8}, then map2 is {0:6, 1:8, 2:0, 3:2, 4:4, 5:5, 6:7, 7:9, 8:1, 9:3}.

## Software Components

### 1. `imei_to_unlock_code.py`

This script generates an 8-digit unlock code from a provided IMEI using a predefined transform map which is used on the Hisense H220m.

**Usage**:

```bash
python imei_to_unlock_code.py <IMEI>
```

- `<IMEI>`: The IMEI string (minimum 15 characters).

**Example**:

```bash
python imei_to_unlock_code.py 987654321098767
```

**Output**: An 8-digit unlock code, e.g., `16159363`.

Execute `python imei_to_unlock_code.py -h` for additional details.

### 2. `compute_transform_map.py`

This script computes possible transform maps from at least two IMEI:unlock_code pairs using the Z3 solver.

**Usage**:

```bash
python compute_transform_map.py <IMEI1:unlock_code1> <IMEI2:unlock_code2> ...
```

- `<IMEI:unlock_code>`: Pairs of IMEI and 8-digit unlock code, separated by a colon.

**Example**:

```bash
python compute_transform_map.py 010203040506071:88552291 123456789012347:61739633
```

**Output**:

```
Found 2 possible transform maps:
Solution 1: {0: 1, 1: 3, 2: 5, 3: 7, 4: 9, 5: 0, 6: 2, 7: 4, 8: 6, 9: 8}
Solution 2: {0: 6, 1: 8, 2: 0, 3: 2, 4: 4, 5: 5, 6: 7, 7: 9, 8: 1, 9: 3}
```

Execute `python compute_transform_map.py -h` for additional details.

## Installation

Required dependencies are installed via:

```bash
pip install -r requirements.txt
```

`requirements.txt`:

```
z3-solver
```

## Notes

- Transform maps may vary across devices or firmware versions. The `compute_transform_map.py` script should be used with pairs specific to the target device.

## References

- ZXIC ZX297520V3 and ZX234220A1. Available: https://www.acwifi.net/16001.html
- FM25LS01 Datasheet. Available: https://eng.fmsh.com/nvm/FM25LS01_ds_eng.pdf
- Realtek RTL8189ES. Available: https://www.realtek.com/en/products/communications-network-ics/item/rtl8189es
- SMMI S5643-51. Available: https://www.smartermicro.com/en/products/s5643-51/
- ETA40543 Datasheet. Available: http://www.eta-semi.com/wp-content/uploads/2022/03/ETA40543_V1.4.pdf
