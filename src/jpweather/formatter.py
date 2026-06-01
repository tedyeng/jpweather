from datetime import datetime
from typing import Dict, Any, List
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.text import Text
from rich.box import ROUNDED

console = Console()

# Weather Code (WMO) Mapping to (Description, Emoji, Color)
WMO_CODES = {
    0: ("晴天 / Clear Sky", "☀️", "yellow"),
    1: ("晴間 / Mainly Clear", "🌤️", "yellow"),
    2: ("多雲 / Partly Cloudy", "⛅", "bright_blue"),
    3: ("陰天 / Overcast", "☁️", "grey53"),
    45: ("有霧 / Fog", "🌫️", "grey70"),
    48: ("霧淞 / Depositing Rime Fog", "🌫️", "grey70"),
    51: ("輕微毛毛雨 / Light Drizzle", "🌧️", "cyan"),
    53: ("中度毛毛雨 / Moderate Drizzle", "🌧️", "cyan"),
    55: ("重度毛毛雨 / Dense Drizzle", "🌧️", "cyan"),
    56: ("輕微凍雨 / Light Freezing Drizzle", "🌨️", "blue"),
    57: ("重度凍雨 / Dense Freezing Drizzle", "🌨️", "blue"),
    61: ("微雨 / Slight Rain", "🌧️", "sky_blue1"),
    63: ("中雨 / Moderate Rain", "🌧️", "dodger_blue1"),
    65: ("大雨 / Heavy Rain", "🌧️", "blue1"),
    66: ("微凍雨 / Light Freezing Rain", "🌨️", "blue"),
    67: ("大凍雨 / Heavy Freezing Rain", "🌨️", "blue"),
    71: ("微雪 / Slight Snow", "❄️", "bright_white"),
    73: ("中雪 / Moderate Snow", "❄️", "bright_white"),
    75: ("大雪 / Heavy Snow", "❄️", "bright_white"),
    77: ("雪粒 / Snow Grains", "❄️", "bright_white"),
    80: ("微陣雨 / Slight Rain Showers", "🌦️", "cyan"),
    81: ("中陣雨 / Moderate Rain Showers", "🌦️", "dodger_blue1"),
    82: ("暴陣雨 / Violent Rain Showers", "⛈️", "purple"),
    85: ("微陣雪 / Slight Snow Showers", "🌨️", "bright_white"),
    86: ("大陣雪 / Heavy Snow Showers", "🌨️", "bright_white"),
    95: ("雷雨 / Thunderstorm", "⛈️", "red"),
    96: ("雷雨伴有微冰雹 / Thunderstorm with Hail", "⛈️", "red"),
    99: ("雷雨伴有大冰雹 / Thunderstorm with Heavy Hail", "⛈️", "red"),
}

def get_weather_info(code: int) -> tuple:
    """Return description, emoji, and color for a WMO weather code."""
    desc, emoji, color = WMO_CODES.get(code, ("未知天氣 / Unknown", "❓", "white"))
    if isinstance(emoji, str):
        emoji = emoji.replace("\ufe0f", "")
    return desc, emoji, color

def get_wind_direction_arrow(degrees: float) -> str:
    """Convert wind degrees to a directional arrow icon."""
    if degrees is None:
        return ""
    arrows = ["↓", "↙", "←", "↖", "↑", "↗", "→", "↘"]
    idx = int((degrees + 22.5) / 45) % 8
    return arrows[idx]

def get_uv_level(uv: float) -> tuple:
    """Get UV hazard text and color."""
    if uv is None:
        return "未知", "white"
    if uv < 3:
        return "低 / Low", "green"
    elif uv < 6:
        return "中 / Moderate", "yellow"
    elif uv < 8:
        return "高 / High", "orange1"
    elif uv < 11:
        return "甚高 / Very High", "red"
    else:
        return "極高 / Extreme", "purple"

def get_weekday_ch(date_str: str) -> str:
    """Get Chinese weekday abbreviation."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekdays = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
        return weekdays[dt.weekday()]
    except Exception:
        return ""

def format_location_title(loc: Dict[str, Any]) -> str:
    """Generate a clean, beautiful display name for a location."""
    name = loc.get("name")
    admin1 = loc.get("admin1")
    country = loc.get("country", "日本")
    
    parts = []
    if name:
        parts.append(name)
    if admin1 and admin1 != name:
        parts.append(admin1)
    if country:
        parts.append(country)
        
    return ", ".join(parts)

def select_location_interactive(locations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Prompt the user to select from multiple locations using questionary.
    """
    choices = []
    for loc in locations:
        title = format_location_title(loc)
        lat = loc.get("latitude", 0.0)
        lon = loc.get("longitude", 0.0)
        timezone = loc.get("timezone", "Asia/Tokyo")
        population = loc.get("population")
        
        pop_str = f" | 人口: {population:,}" if population else ""
        display_str = f"{title} (緯度: {lat:.2f}, 經度: {lon:.2f}{pop_str})"
        
        choices.append(questionary.Choice(title=display_str, value=loc))
        
    # Add a cancel option
    choices.append(questionary.Choice(title="❌ 取消查詢 / Cancel", value=None))
    
    selected = questionary.select(
        "🔍 找到多個地點，請選擇正確的查詢目標：",
        choices=choices,
        style=questionary.Style([
            ('qmark', 'fg:#FF9D00 bold'),
            ('question', 'bold fg:#ffffff'),
            ('pointer', 'fg:#00D7FF bold'),
            ('highlighted', 'fg:#00D7FF bold'),
            ('selected', 'fg:#00FF66'),
        ])
    ).ask()
    
    if not isinstance(selected, dict):
        return {"cancelled": True}
    return selected

def render_current_weather(loc: Dict[str, Any], weather_data: Dict[str, Any], mobile: bool = False):
    """
    Render a stunning visual panel for the current weather.
    """
    if mobile:
        mobile_console = Console(width=38)
        
        current = weather_data.get("current", {})
        temp = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        apparent = current.get("apparent_temperature")
        precip = current.get("precipitation", 0.0)
        wcode = current.get("weather_code", 0)
        wind_spd = current.get("wind_speed_10m")
        wind_dir = current.get("wind_direction_10m")
        
        desc, emoji, color = get_weather_info(wcode)
        loc_title = format_location_title(loc)
        tz = weather_data.get("timezone", loc.get("timezone", "Asia/Tokyo"))
        
        # Stacking all text vertically to fit inside 38 columns (content width 32)
        full_text = Text()
        full_text.append(strip_vs16(f"📍 {loc_title}\n"), style="bold cyan")
        full_text.append(strip_vs16(f"🌐 緯度: {loc.get('latitude'):.2f} 經度: {loc.get('longitude'):.2f}\n"), style="dim")
        full_text.append(strip_vs16(f"⏰ 時區: {tz}\n\n"), style="dim")
        full_text.append(strip_vs16(f"{emoji}  {temp}°C  {desc.split(' / ')[0]}\n\n"), style=f"bold {color}")
        
        full_text.append(strip_vs16(f"體感 Apparent : {apparent}°C\n"), style="white")
        full_text.append(strip_vs16(f"濕度 Humidity : {humidity}%\n"), style="white")
        
        wind_arrow = get_wind_direction_arrow(wind_dir)
        full_text.append(strip_vs16(f"風速 Wind Spd : {wind_spd} m/s {wind_arrow}\n"), style="white")
        full_text.append(strip_vs16(f"降雨 Rain     : {precip} mm\n"), style="white")
        
        panel = Panel(
            full_text,
            title=strip_vs16(f"🌦️ {loc.get('name', 'GPS')} 目前天氣"),
            border_style="bright_blue",
            box=ROUNDED,
            width=38
        )
        mobile_console.print(panel)
        
        # Hourly forecast (narrow table)
        hourly = weather_data.get("hourly", {})
        if hourly and "time" in hourly:
            current_time = current.get("time")
            times = hourly.get("time", [])
            
            start_idx = 0
            current_hour_time = current_time
            if current_time and len(current_time) >= 16:
                current_hour_time = current_time[:14] + "00"
                
            if current_hour_time in times:
                start_idx = times.index(current_hour_time)
                
            mobile_console.print("\n[bold yellow]🕒 3小時預報 Hourly Forecast[/bold yellow]")
            
            for step in range(8):
                idx = start_idx + (step * 3)
                if idx >= len(times):
                    break
                    
                time_str = times[idx]
                temp_val = hourly.get("temperature_2m", [])[idx]
                wcode_val = hourly.get("weather_code", [])[idx]
                pop_val = hourly.get("precipitation_probability", [])[idx]
                
                try:
                    dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M")
                    t_lbl = dt.strftime("%H:%M")
                except Exception:
                    t_lbl = time_str
                    
                if step == 0:
                    time_display = f"{t_lbl}*"
                else:
                    time_display = t_lbl
                    
                desc_val, emoji_val, color_val = get_weather_info(wcode_val)
                weather_display = f"{emoji_val} {desc_val.split(' / ')[0]}"
                temp_display = f"{temp_val:.1f}°C"
                pop_display = f"{pop_val}%" if pop_val is not None else "-"
                
                # Format as a clean, compact single line
                line = Text()
                line.append(f"● {time_display} ", style="cyan")
                line.append(f"{weather_display} ", style=color_val)
                line.append(f"{temp_display} ", style="white")
                line.append(f"{pop_display}", style="grey70")
                
                mobile_console.print(strip_vs16(line))
        return

    current = weather_data.get("current", {})
    temp = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    apparent = current.get("apparent_temperature")
    precip = current.get("precipitation", 0.0)
    wcode = current.get("weather_code", 0)
    wind_spd = current.get("wind_speed_10m")
    wind_dir = current.get("wind_direction_10m")
    
    desc, emoji, color = get_weather_info(wcode)
    loc_title = format_location_title(loc)
    tz = weather_data.get("timezone", loc.get("timezone", "Asia/Tokyo"))
    
    # 1. Location Header (Clean separate block)
    header_text = Text()
    header_text.append(f"\n📍 {loc_title}\n", style="bold cyan")
    gps_info = f"🌐 緯度: {loc.get('latitude'):.4f}  經度: {loc.get('longitude'):.4f}"
    if loc.get("elevation"):
        gps_info += f"  海拔: {loc.get('elevation')}m"
    gps_info += f"  時區: {tz}"
    header_text.append(gps_info, style="dim")
    console.print(header_text)
    
    # 2. Main Weather Status Panel (Clean compact side-by-side layout)
    # Left column: Temp & Weather description
    temp_text = Text()
    temp_text.append(f"\n  {emoji}  {temp}°C\n\n", style=f"bold {color}")
    temp_text.append(f"  目前天氣：\n  {desc}\n", style=f"bold {color}")
    
    # Right column: Stats table
    # Right column: Stats table
    wind_arrow = get_wind_direction_arrow(wind_dir)
    stats_table = Table.grid(padding=(0, 1))
    stats_table.add_column(style="dim", width=26)
    stats_table.add_column(style="bold white", width=12)
    
    stats_table.add_row("體感溫度 Apparent Temp :", f"{apparent}°C")
    stats_table.add_row("相對濕度 Humidity      :", f"{humidity}%")
    stats_table.add_row("風速風向 Wind Speed    :", f"{wind_spd} m/s {wind_arrow}")
    stats_table.add_row("目前降雨 Precipitation :", f"{precip} mm")
    
    # Layout Grid to align Left and Right side-by-side inside the panel
    layout_grid = Table.grid(padding=(0, 2))
    layout_grid.add_column(width=22)
    layout_grid.add_column(width=38)
    layout_grid.add_row(temp_text, stats_table)
    
    panel = Panel(
        layout_grid,
        title=strip_vs16("[bold yellow]🌦️ 目前天氣狀態 Current Weather[/bold yellow]"),
        border_style="bright_blue",
        box=ROUNDED,
        width=68,
        padding=(1, 2)
    )
    console.print(panel)
    
    # Render Hourly Table if data is available
    hourly = weather_data.get("hourly", {})
    if hourly and "time" in hourly:
        current_time = current.get("time")  # e.g. "2026-05-31T11:45"
        times = hourly.get("time", [])
        
        # Open-Meteo current time has 15-minute intervals (e.g. 11:45), 
        # while hourly times are on the hour (e.g. 11:00). We normalize to clean hour.
        start_idx = 0
        current_hour_time = current_time
        if current_time and len(current_time) >= 16:
            current_hour_time = current_time[:14] + "00"
            
        if current_hour_time in times:
            start_idx = times.index(current_hour_time)
            
        console.print("\n[bold yellow]🕒 近期每 3 小時預報 Hourly Forecast (Next 24h)[/bold yellow]")
        
        hourly_table = Table(box=ROUNDED, border_style="bright_blue", header_style="bold cyan")
        hourly_table.add_column("時間 Time", justify="left")
        hourly_table.add_column("天氣 Weather", justify="left")
        hourly_table.add_column("氣溫 Temp", justify="right")
        hourly_table.add_column("降雨機率 Pop", justify="right")
        
        for step in range(8):
            idx = start_idx + (step * 3)
            if idx >= len(times):
                break
                
            time_str = times[idx]
            temp = hourly.get("temperature_2m", [])[idx]
            wcode = hourly.get("weather_code", [])[idx]
            pop = hourly.get("precipitation_probability", [])[idx]
            
            try:
                dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M")
                t_lbl = dt.strftime("%H:%M")
            except Exception:
                t_lbl = time_str
                
            if step == 0:
                time_display = f"{t_lbl} [bold yellow](現在)[/bold yellow]"
            else:
                time_display = f"{t_lbl} [dim](+{step * 3}h)[/dim]"
                
            desc, emoji, color = get_weather_info(wcode)
            weather_display = f"{emoji} [bold {color}]{desc}[/bold {color}]"
            temp_display = f"[bold white]{temp:.1f}°C[/bold white]"
            
            if pop is not None:
                if pop >= 70:
                    pop_display = f"[bold dodger_blue1]{pop}% 🌧️[/bold dodger_blue1]"
                elif pop >= 30:
                    pop_display = f"[sky_blue1]{pop}% 🌦️[/sky_blue1]"
                else:
                    pop_display = f"[grey53]{pop}%[/grey53]"
            else:
                pop_display = "[dim]-[/dim]"
                
            hourly_table.add_row(
                strip_vs16(time_display),
                strip_vs16(weather_display),
                strip_vs16(temp_display),
                strip_vs16(pop_display)
            )
            
        console.print(hourly_table)

def strip_vs16(text: str) -> str:
    """Strip variation selector-16 (U+FE0F) which causes terminal border misalignment."""
    if isinstance(text, str):
        return text.replace("\ufe0f", "")
    return text

def render_forecast_weather(loc: Dict[str, Any], weather_data: Dict[str, Any], mobile: bool = False):
    """
    Render a stunning visual table for the 7-day forecast.
    Includes visual temperature bars.
    """
    daily = weather_data.get("daily", {})
    if not daily:
        console.print("[red]無法取得預報資料！[/red]")
        return
        
    loc_title = format_location_title(loc)
    
    if mobile:
        mobile_console = Console(width=38)
        mobile_console.print(f"\n[bold yellow]📅 7 天天氣預報 7-Day Outlook[/bold yellow]")
        mobile_console.print(f"[cyan]📍 {loc_title}[/cyan]")
        mobile_console.print(f"更新: {datetime.now().strftime('%m-%d %H:%M')}\n")
        
        for i in range(len(daily.get("time", []))):
            date_str = daily["time"][i]
            wcode = daily["weather_code"][i]
            tmin = daily["temperature_2m_min"][i]
            tmax = daily["temperature_2m_max"][i]
            precip_sum = daily["precipitation_sum"][i]
            pop = daily.get("precipitation_probability_max", [None])[i]
            uv = daily.get("uv_index_max", [None])[i]
            
            weekday = get_weekday_ch(date_str)
            desc, emoji, color = get_weather_info(wcode)
            
            card = Text()
            card.append(f"● {date_str} ({weekday}) {emoji} {desc.split(' / ')[0]}\n", style=f"bold {color}")
            
            card.append("  🌡️ 氣溫: ")
            card.append(f"{tmin:.1f}°C", style="blue")
            card.append(" ~ ")
            card.append(f"{tmax:.1f}°C", style="red")
            card.append("\n")
            
            pop_str = f"{pop}%" if pop is not None else "-"
            rain_str = f"{precip_sum:.1f} mm" if precip_sum > 0 else "0.0 mm"
            card.append(f"  🌧️ 降雨: {pop_str} | {rain_str}\n")
            
            card.append("  ☀️ 紫外線: ")
            if uv is not None:
                uv_lbl, uv_color = get_uv_level(uv)
                card.append(f"{uv:.1f} ({uv_lbl.split(' / ')[0]})", style=uv_color)
            else:
                card.append("-")
            
            # Print as beautiful borderless paragraph blocks with a separating newline
            mobile_console.print(card)
            mobile_console.print()
        return
    
    # Title Header
    tz = weather_data.get("timezone", loc.get("timezone", "Asia/Tokyo"))
    console.print(f"\n[bold yellow]📅 7 天天氣預報 7-Day Outlook[/bold yellow] : [cyan]{loc_title}[/cyan]")
    console.print(f"時區 Timezone: {tz} | 更新時間 Update Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    table = Table(box=ROUNDED, border_style="bright_blue", header_style="bold cyan")
    table.add_column("日期 Date", justify="left")
    table.add_column("天氣 Weather", justify="left")
    table.add_column("降雨機率 Pop", justify="right")
    table.add_column("累積降雨 Rain", justify="right")
    table.add_column("紫外線 UV", justify="center")
    table.add_column("氣溫變化 Temp Range", justify="center")
    

        
    for i in range(len(daily.get("time", []))):
        date_str = daily["time"][i]
        wcode = daily["weather_code"][i]
        tmin = daily["temperature_2m_min"][i]
        tmax = daily["temperature_2m_max"][i]
        precip_sum = daily["precipitation_sum"][i]
        pop = daily.get("precipitation_probability_max", [None])[i] # Some models might have None
        uv = daily.get("uv_index_max", [None])[i]
        
        # Format Date
        weekday = get_weekday_ch(date_str)
        date_display = f"{date_str} ({weekday})"
        
        # Format Weather
        desc, emoji, color = get_weather_info(wcode)
        weather_display = f"{emoji} [bold {color}]{desc}[/bold {color}]"
        
        # Format POP (Precipitation Probability)
        if pop is not None:
            if pop >= 70:
                pop_display = f"[bold dodger_blue1]{pop}% 🌧️[/bold dodger_blue1]"
            elif pop >= 30:
                pop_display = f"[sky_blue1]{pop}% 🌦️[/sky_blue1]"
            else:
                pop_display = f"[grey53]{pop}%[/grey53]"
        else:
            pop_display = "[dim]-[/dim]"
            
        # Format Precipitation Sum
        if precip_sum > 0:
            precip_display = f"[bold cyan]{precip_sum:.1f} mm[/bold cyan]"
        else:
            precip_display = "[dim]0.0 mm[/dim]"
            
        # Format UV
        if uv is not None:
            uv_lbl, uv_color = get_uv_level(uv)
            uv_display = f"[{uv_color}]{uv:.1f} ({uv_lbl})[/{uv_color}]"
        else:
            uv_display = "[dim]-[/dim]"
            
        # Format Temperature Range
        temp_bar = f"[blue]{tmin:.1f}°C[/blue] [dim]~[/dim] [red]{tmax:.1f}°C[/red]"
        
        table.add_row(
            strip_vs16(date_display),
            strip_vs16(weather_display),
            strip_vs16(pop_display),
            strip_vs16(precip_display),
            strip_vs16(uv_display),
            strip_vs16(temp_bar)
        )
        
    console.print(table)
