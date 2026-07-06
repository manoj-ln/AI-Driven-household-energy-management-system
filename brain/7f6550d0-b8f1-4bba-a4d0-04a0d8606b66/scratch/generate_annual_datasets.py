
import csv
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
import json

# Import the precalculate logic locally to avoid side effects
def precalculate_for_file(file_path):
    import sys
    sys.path.append(r'c:\myproject\backend')
    from app.services.dataset_cache_service import DatasetCacheService

    print(f"Precalculating cache for {file_path.name}...")
    rows = DatasetCacheService.load_csv(file_path)
    if not rows: return
    
    start_ts = rows[0]['timestamp']
    end_ts = rows[-1]['timestamp']
    coverage_days = (end_ts - start_ts).total_seconds() / 86400.0
    
    daily_aggregated = {}
    for row in rows:
        date_str = row['timestamp'].date().isoformat()
        if date_str not in daily_aggregated:
            daily_aggregated[date_str] = {"total": 0.0, "temp": 0.0, "count": 0}
        daily_aggregated[date_str]["total"] += row['total_consumption']
        daily_aggregated[date_str]["temp"] += row['temperature']
        daily_aggregated[date_str]["count"] += 1
    
    daily_history = []
    for date_str in sorted(daily_aggregated.keys()):
        data = daily_aggregated[date_str]
        daily_history.append({
            "date": date_str,
            "total_consumption": round(data["total"], 3),
            "average_temperature": round(data["temp"] / data["count"], 1)
        })

    current_month = datetime.now().month
    seasons = {"☀️ Summer": (3, 4, 5), "🌧️ Monsoon": (6, 7, 8, 9), "🍂 Post-Monsoon": (10, 11), "❄️ Winter": (12, 1, 2)}
    dominant_season = "Unknown"
    for s, m_list in seasons.items():
        if current_month in m_list:
            dominant_season = s
            break

    metadata = {
        "row_count": len(rows),
        "start": start_ts.isoformat(),
        "end": end_ts.isoformat(),
        "coverage_days": round(coverage_days, 2),
        "daily_history": daily_history,
        "pattern_insights": {"dominant_season": dominant_season, "quality_score": 99}
    }
    with open(file_path.with_suffix('.cache.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f)

def generate_year(year):
    output_dir = Path(r'c:\myproject\backend\data\datasets')
    output_file = output_dir / f'energy_dataset_{year}.csv'
    
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    current_time = start_date
    delta = timedelta(minutes=10)

    device_configs = {
        "Fridge": (0.15, 1.0, (10, 10), "Always-On-Cycle"),
        "WiFi_Router": (0.015, 1.0, (10, 10), "Always-On"),
        "AC_Main": (1.5, 0.0, (60, 240), "Season-Cooling"),
        "Heater": (1.2, 0.0, (30, 120), "Season-Heating"),
        "Coffee_Grinder": (0.4, 0.05, (1, 2), "Intermittent-Morning"),
        "Microwave": (0.8, 0.1, (2, 5), "Intermittent-Mealtime"),
        "Washing_Machine": (0.5, 0.02, (45, 90), "Duration-Weekend"),
        "Living_Room_TV": (0.12, 0.3, (60, 180), "Evening"),
        "LED_Lights": (0.06, 0.0, (180, 360), "Temporal-Evening")
    }
    active_durations = {name: 0 for name in device_configs}

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'temperature', 'humidity', 'total_consumption'] + list(device_configs.keys()))

        while current_time < end_date:
            month = current_time.month
            hour = current_time.hour
            is_weekend = current_time.weekday() >= 5
            
            base_temp = 22 + 5 * math.sin((month - 1) * math.pi / 6)
            hourly_variation = -5 * math.cos(hour * math.pi / 12)
            temp = base_temp + hourly_variation + random.uniform(-1, 1)
            humidity = 50 + random.uniform(-5, 5)

            total = 0.0
            row_vals = []
            for name, config in device_configs.items():
                base_p, prob, dur, cat = config
                consumption = 0.0
                if active_durations[name] > 0:
                    active_durations[name] -= 10
                    consumption = base_p
                else:
                    trigger = False
                    if cat == "Always-On": consumption = base_p
                    elif cat == "Always-On-Cycle" and random.random() < 0.3: consumption = base_p
                    elif cat == "Intermittent-Morning" and 7 <= hour <= 9 and random.random() < 0.1: trigger = True
                    elif cat == "Intermittent-Mealtime" and (7<=hour<=9 or 12<=hour<=14 or 19<=hour<=21) and random.random() < 0.15: trigger = True
                    elif cat == "Season-Cooling" and temp > 28 and random.random() < 0.2: trigger = True
                    elif cat == "Season-Heating" and temp < 18 and random.random() < 0.2: trigger = True
                    elif cat == "Duration-Weekend" and is_weekend and 8 <= hour <= 16 and random.random() < 0.05: trigger = True
                    elif cat == "Temporal-Evening" and 18 <= hour <= 23: consumption = base_p
                    elif cat == "Evening" and 18 <= hour <= 23 and random.random() < 0.3: trigger = True
                    
                    if trigger:
                        active_durations[name] = random.randint(dur[0], dur[1])
                        consumption = base_p
                
                energy = (consumption * 10) / 60
                if is_weekend: energy *= 1.2
                total += energy
                row_vals.append(round(energy, 4))

            writer.writerow([current_time.strftime('%Y-%m-%d %H:%M:%S'), round(temp, 1), round(humidity, 1), round(total, 4)] + row_vals)
            current_time += delta
            
    print(f"Generated energy_dataset_{year}.csv")
    precalculate_for_file(output_file)

if __name__ == "__main__":
    for y in [2021, 2024, 2025]:
        generate_year(y)
