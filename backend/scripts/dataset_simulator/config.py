"""Scenario configuration + shared output schema for the simulator."""

from dataclasses import dataclass, field

# Rich per-minute metadata columns, shared across all datasets.
# These will also be treated as metadata (not devices) by the backend cache.
META_COLUMNS = [
    "timestamp", "Year", "Month", "Week", "Day", "DayOfWeek", "Hour", "Minute",
    "Season", "Weather", "Temperature", "Humidity", "OccupancyLevel",
    "ElectricityTariff", "RenewableEnergyStatus", "PowerOutageStatus",
    "DeviceStatus", "DevicePowerConsumption", "TotalHouseholdConsumption",
    "EstimatedCost", "CarbonEmissions", "AnomalyLabel",
    # Smart-eco household extra columns (empty/blank in other datasets)
    "SolarGeneration", "BatterySOC", "GridImport", "GridExport",
]


@dataclass
class Scenario:
    name: str
    label: str
    years: list[int]
    power_flags: dict[str, bool]
    electricity_tariff: str
    uses_renewables: bool = False
    base_cost_pu: float = 6.26    # default per-unit price in INR/kWh
    note: str = ""


def _flags(**kwargs: bool) -> dict[str, bool]:
    return kwargs


def _all_flags() -> dict[str, bool]:
    """Default: every device in the catalog enabled."""
    from .devices import DEVICE_CATALOG
    return {name: True for name in DEVICE_CATALOG}


WORKING_FLAGS = _flags(
    Ceiling_Fan_Living=True, Ceiling_Fan_Bed1=True, Ceiling_Fan_Bed2=True,
    Ceiling_Fan_Kitchen=True, Table_Fan_Study=True, Pedestal_Fan_Stand=True,
    Exhaust_Fan_Kitchen=True, Exhaust_Fan_Bath=True,
    Air_Conditioner_Bed1=True, Air_Conditioner_Living=True, Air_Conditioner_Study=True,
    Refrigerator_Main=True, Refrigerator_Secondary=True, Water_Purifier_Kitchen=True,
    Microwave_Oven=True, Induction_Stove_1=True, Induction_Stove_2=True,
    Rice_Cooker=True, Electric_Kettle=True, Coffee_Machine=True, Mixer_Grinder=True,
    Toaster=True, Electric_Chimney=True, Air_Fryer=True, Dishwasher=True,
    Bottle_Warmer=True,
    Washing_Machine=True, Iron_Box=True, Vacuum_Cleaner=True, Robot_Vacuum=True,
    Geyser_Bathroom1=True, Geyser_Bathroom2=True, Water_Heater_Kitchen=True,
    Room_Heater_Bed1=True, Room_Heater_Bed2=True,
    Water_Pump_Overhead=True, Aquarium_Pump=True, Aquarium_Heater=True,
    Television_Living=True, Television_Second=True, Home_Theater_Speaker=True,
    Soundbar_Living=True, Projector=True, Gaming_Console=True,
    Desktop_PC=True, Laptop_1=True, Laptop_2=True, Monitor_1=True, Monitor_2=True,
    Printer=True, WiFi_Router=True,
    LED_Lights_Living=True, LED_Lights_Kitchen=True, LED_Lights_Bed1=True,
    LED_Lights_Bed2=True, LED_Lights_Study=True, LED_Lights_Bathroom=True,
    LED_Lights_Corridor=True, LED_Lights_Outdoor=True, Garden_Lights=True,
    Security_Lights=True, Security_Lights_Backyard=True, Festival_String_Lights=True,
    Phone_Charger_1=True, Phone_Charger_2=True, Phone_Charger_3=True,
    Tablet_Charger_1=True, Tablet_Charger_2=True, Smartwatch_Charger_1=True,
    Smartwatch_Charger_2=True, Laptop_Charger_1=True, Laptop_Charger_2=True,
    EV_Charger_Wall=True, UPS_Backup=True,
    Smart_Speaker_Living=True, Smart_Speaker_Bed=True, Smart_Hub=True,
    Smart_Plug_1=True, Smart_Plug_2=True, Smart_Doorbell=True, Smart_Lock=True,
    CCTV_Camera_1=True, CCTV_Camera_2=True,
    Smart_Curtains_Living=True, Smart_Curtains_Bed=True,
    Air_Purifier=True, Humidifier=True, CPAP_Machine=True, Treadmill=True,
    Hair_Dryer=True, Electric_Shaver=True, Electric_Toothbrush=True,
    Garage_Door_Motor=True,
    Vacuum_Charger_Base=True,
    Smart_Display_Kitchen=True,
)

BUSINESS_FLAGS = _flags(
    Ceiling_Fan_Living=True, Ceiling_Fan_Kitchen=True, Table_Fan_Study=True,
    Exhaust_Fan_Kitchen=True, Exhaust_Fan_Bath=True, Exhaust_Fan_Attic=True,
    Air_Conditioner_Bed1=True, Air_Conditioner_Living=True, Air_Conditioner_Study=True,
    Air_Cooler_Outdoor=True,
    Refrigerator_Main=True, Deep_Freezer=True, Mini_Fridge_Bed=True,
    Water_Purifier_Kitchen=True,
    Microwave_Oven=True, Electric_Oven=True, Induction_Stove_1=True,
    Rice_Cooker=True, Electric_Kettle=True, Coffee_Machine=True, Mixer_Grinder=True,
    Electric_Chimney=True, Air_Fryer=True, Dishwasher=True,
    Washing_Machine=True, Clothes_Dryer=True, Iron_Box=True, Vacuum_Cleaner=True,
    Geyser_Bathroom1=True, Water_Heater_Kitchen=True, Room_Heater_Bed1=True,
    Water_Pump_Overhead=True, Water_Pump_Borewell=True,
    Television_Living=True, Television_Second=True, Home_Theater_Speaker=True,
    Desktop_PC=True, Desktop_PC_2=True, Monitor_1=True, Monitor_2=True,
    Printer=True, Photocopier=True, WiFi_Router=True, Server_NAS=True,
    Network_Switch=True, Video_Conference_System=True,
    LED_Lights_Living=True, LED_Lights_Kitchen=True, LED_Lights_Bed1=True,
    LED_Lights_Study=True, LED_Lights_Bathroom=True, LED_Lights_Corridor=True,
    LED_Lights_Outdoor=True, Garden_Lights=True, Security_Lights=True,
    Security_Lights_Backyard=True, Festival_String_Lights=True,
    Phone_Charger_1=True, Phone_Charger_2=True, Tablet_Charger_1=True,
    Smartwatch_Charger_1=True, EV_Charger_Office=True,
    Power_Tool_Charger=True, Drone_Charger=True, UPS_Backup=True,
    Generator=True, Battery_Backup_UPS=True,
    Smart_Speaker_Living=True, Smart_Hub=True, Smart_Plug_1=True, Smart_Plug_2=True,
    Smart_Doorbell=True, Smart_Lock=True, CCTV_Camera_1=True, CCTV_Camera_2=True,
    CCTV_Camera_3=True, Air_Purifier=True, Electric_Shaver=True,
    Electric_Gate_Motor=True, Sewing_Machine=True, Smart_Display_Kitchen=True,
)

ECO_FLAGS = _flags(
    Ceiling_Fan_Living=True, Ceiling_Fan_Bed1=True, Ceiling_Fan_Bed2=True,
    Ceiling_Fan_Kitchen=True, Table_Fan_Study=True, Pedestal_Fan_Stand=True,
    Exhaust_Fan_Kitchen=True, Exhaust_Fan_Bath=True,
    Air_Conditioner_Bed1=True, Air_Conditioner_Living=True, Air_Conditioner_Study=True,
    Refrigerator_Main=True, Water_Purifier_Kitchen=True,
    Microwave_Oven=True, Induction_Stove_1=True, Induction_Stove_2=True,
    Rice_Cooker=True, Electric_Kettle=True, Coffee_Machine=True, Mixer_Grinder=True,
    Electric_Chimney=True, Air_Fryer=True, Dishwasher=True,
    Washing_Machine=True, Clothes_Dryer=True, Iron_Box=True, Robot_Vacuum=True,
    Geyser_Bathroom1=True, Geyser_Bathroom2=True,
    Water_Pump_Overhead=True, Aquarium_Pump=True, Aquarium_Heater=True,
    Television_Living=True, Television_Second=True, Soundbar_Living=True,
    Laptop_1=True, Laptop_2=True, Monitor_1=True, Monitor_2=True,
    Printer=True, WiFi_Router=True,
    LED_Lights_Living=True, LED_Lights_Kitchen=True, LED_Lights_Bed1=True,
    LED_Lights_Bed2=True, LED_Lights_Study=True, LED_Lights_Bathroom=True,
    LED_Lights_Corridor=True, LED_Lights_Outdoor=True, Garden_Lights=True,
    Security_Lights=True, Security_Lights_Backyard=True, Festival_String_Lights=True,
    Phone_Charger_1=True, Phone_Charger_2=True, Tablet_Charger_1=True,
    Smartwatch_Charger_1=True, Laptop_Charger_1=True, EV_Charger_Wall=True,
    Smart_Speaker_Living=True, Smart_Speaker_Bed=True, Smart_Hub=True,
    Smart_Display_Kitchen=True, Smart_Plug_1=True, Smart_Plug_2=True,
    Smart_Doorbell=True, Smart_Lock=True, CCTV_Camera_1=True, CCTV_Camera_2=True,
    Smart_Curtains_Living=True, Smart_Curtains_Bed=True,
    Motion_Sensor_Living=True, Motion_Sensor_Kitchen=True, Motion_Sensor_Corridor=True,
    Smart_Thermostat=True, Air_Purifier_Living=True,
    Solar_Inverter=True, Battery_Storage=True, UPS_Backup=True,
)

# Smallest set of always-needed appliances for the 2021-style reference year.
BASE_YEAR_FLAGS = _flags(
    Refrigerator_Main=True, Television_Living=True, Ceiling_Fan_Living=True,
    Ceiling_Fan_Bed1=True, Phone_Charger_1=True, Exhaust_Fan_Bath=True,
    Iron_Box=True, Geyser_Bathroom1=True, LED_Lights_Living=True,
    LED_Lights_Kitchen=True, LED_Lights_Bed1=True, LED_Lights_Bathroom=True,
    LED_Lights_Outdoor=True, Microwave_Oven=True, Induction_Stove_1=True,
    Electric_Kettle=True, Mixer_Grinder=True, Water_Purifier_Kitchen=True,
    Washing_Machine=True, Water_Pump_Overhead=True, Television_Second=True,
    Desktop_PC=True, Laptop_1=True, Monitor_1=True, WiFi_Router=True,
    Printer=True, Smart_Hub=True, Smart_Speaker_Living=True, Smart_Doorbell=True,
    Smart_Lock=True, CCTV_Camera_1=True, Ceiling_Fan_Kitchen=True,
    Table_Fan_Study=True, Room_Heater_Bed1=True, UPS_Backup=True,
    LED_Lights_Study=True, LED_Lights_Corridor=True, Coffee_Machine=True,
    Rice_Cooker=True, Toaster=True, Electric_Chimney=True, Air_Fryer=True,
)


SCENARIOS: dict[str, Scenario] = {
    "working": Scenario(
        name="working",
        label="Dataset_Working_Household",
        years=[2023, 2024, 2025],
        power_flags=WORKING_FLAGS,
        electricity_tariff="residential_slabbed",
        note="Salaried dual-income family with hybrid work, kids, school schedules.",
    ),
    "business": Scenario(
        name="business",
        label="Dataset_Business_Household",
        years=[2024, 2025],
        power_flags=BUSINESS_FLAGS,
        electricity_tariff="commercial_flat",
        base_cost_pu=8.5,
        note="Entrepreneur running a home office with servers, CCTV, generators.",
    ),
    "eco": Scenario(
        name="eco",
        label="Dataset_Smart_Eco_Household",
        years=[2024, 2025],
        power_flags=ECO_FLAGS,
        electricity_tariff="dynamic_toU",
        uses_renewables=True,
        base_cost_pu=6.26,
        note="Modern smart home with solar, battery, EV and demand-response.",
    ),
}
