# Inter-sheet nets for odeck-10. Nets listed here get global labels; everything else is local to its sheet.
# Keep names in sync with docs/nets.md. Power symbols are used for POWER_SYMBOL_NETS.

POWER_SYMBOL_NETS = ["GND"]

GLOBAL_NETS = [
    # --- power rails
    "VIN",            # 9-48 V main input rail after OR-ing (PD-in / barrel)
    "VBUS_LAPTOP",    # laptop USB-C VBUS (source up to 28 V x 5 A, or sink 5 V in bus-powered mode)
    "VBUS_PDIN",      # PD-in USB-C VBUS (sink, up to 48 V)
    "VBUS_DS",        # downstream USB-C VBUS (5 V source)
    "VBB_OUT",        # buck-boost output before laptop source switch (5-28 V)
    "+5V", "+3V3", "+1V15", "+1V1",
    "+5V_USBA1", "+5V_USBA2",
    # --- power-path control / status
    "EXT_PWR_PRESENT",  # high when PD-in or barrel supplies VIN
    "PDIN_PRESENT",     # high when PD-in contract is active (disables barrel path)
    "VBB_PG",           # buck-boost power good
    "VBB_EN",           # buck-boost enable (PMG1)
    "VBB_VSEL0", "VBB_VSEL1", "VBB_VSEL2",  # buck-boost voltage select (PMG1 GPIO only)
    "LAPTOP_SRC_EN",    # PMG1 request to enable source switch to laptop (gated in hardware)
    "LAPTOP_SNK_EN",    # enable bus-power sink switch (laptop VBUS -> +5V), only without ext power
    "LAPTOP_OVP_N",     # hardware OVP trip (active low)
    # --- I2C / SMBus
    "I2C_PD_SCL", "I2C_PD_SDA",     # RP2350 <-> PMG1 (host interface), TPS26750
    "I2C_SYS_SCL", "I2C_SYS_SDA",   # RP2350 <-> sensors, INA2xx, EEPROMs
    "I2C_PD_INT_N", "PDIN_INT_N",
    "HUB_SMB_CLK", "HUB_SMB_DAT", "HUB_SMB_PU", "HUB_RESET_N",
    # --- USB 2.0 / 3.x links between sheets
    "LAPTOP_USB_DP", "LAPTOP_USB_DN",          # laptop USB2 to hub upstream
    "HUB_UP_SS_TXP", "HUB_UP_SS_TXN", "HUB_UP_SS_RXP", "HUB_UP_SS_RXN",
    "DP_ML0_P", "DP_ML0_N", "DP_ML1_P", "DP_ML1_N", "DP_AUX_P", "DP_AUX_N", "DP_HPD",
    # --- PMG1 debug / control from RP2350
    "PMG1_SWDIO", "PMG1_SWCLK", "PMG1_XRES_N",
    # --- misc control
    "USBA1_FORCE_EN", "USBA2_FORCE_EN", "USBA1_ISENSE", "USBA2_ISENSE",
]
