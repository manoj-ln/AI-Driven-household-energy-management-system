from datetime import datetime

def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)

def format_energy(value: float) -> str:
    return f"{value:.2f} kWh"
