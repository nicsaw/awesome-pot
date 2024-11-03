import json
import requests
import re
import pandas as pd
from typing import List, Dict, Set, Any

CACHE_FILENAME = "ip_info_cache.json"
FLASK_LOG_PATTERN = re.compile(r'(?P<ip>(\d{1,3}\.){3}\d{1,3}) - - \[(?P<timestamp>.*?)\] (?P<message>.*)')

def is_json_log(line: str) -> bool:
    try:
        json.loads(line)
        return True
    except json.JSONDecodeError:
        return False

def parse_json_log(line: str) -> Dict[str, Any]:
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        print(f"ERROR parsing {line}")
        return {}

def is_flask_log(line: str) -> bool:
    return bool(FLASK_LOG_PATTERN.match(line))

def parse_flask_log(line: str) -> Dict[str, Any]:
    match = FLASK_LOG_PATTERN.match(line)
    if match:
        return {
            "ip": match.group("ip"),
            "timestamp": match.group("timestamp"),
            "message": match.group("message"),
            "is_flask": True,
        }
    else:
        return {}

def json_to_list(file_path: str) -> List[Dict[str, Any]]:
    log_entries = []
    try:
        with open(file_path, 'r') as log_file:
            for line in log_file:
                line = line.strip()
                if not line:
                    continue

                if is_json_log(line):
                    log_entry = parse_json_log(line)
                    log_entries.append(log_entry)
                elif is_flask_log(line):
                    log_entry = parse_flask_log(line)
                    log_entries.append(log_entry)
                else:
                    continue

    except Exception as e:
        print(f"ERROR reading file {file_path}: {e}")
    return log_entries

def load_ip_info_cache(cache_file: str=CACHE_FILENAME) -> Dict[str, Any]:
    try:
        with open(cache_file, 'r') as f:
            cache = json.load(f)
            print(f"Loaded IP info cache from {cache_file}")
            return cache
    except FileNotFoundError:
        print(f"No cache file found at {cache_file}. Starting with an empty cache.")
        return {}
    except Exception as e:
        print(f"ERROR loading cache: {e}")
        return {}

def save_ip_info_cache(ip_info_cache: Dict[str, Any], cache_file: str = CACHE_FILENAME) -> None:
    try:
        with open(cache_file, 'w') as f:
            json.dump(ip_info_cache, f, indent=4)
            print(f"Saved IP info cache to {cache_file}")
    except Exception as e:
        print(f"ERROR saving cache: {e}")

def get_values(key: str, logs) -> List[Any]:
    return [entry[key] for entry in logs if key in entry]

def get_unique_values(key: str, logs) -> Set[Any]:
    return set(entry[key] for entry in logs if key in entry)

def get_ip_info(ip: str, ip_info_cache: Dict[str, Any]):
    if ip in ip_info_cache:
        return ip_info_cache[ip]
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        data = response.json()
        data.pop("readme", None)
        ip_info_cache[ip] = data
        return data
    except Exception as e:
        print(f"ERROR get_ip_info({ip}): {e}")
        return {}

def add_ip_info(log_entries, ip_info_cache, ip_key="src_ip"):
    unique_ips = get_unique_values(ip_key, log_entries)
    for ip in unique_ips:
        get_ip_info(ip, ip_info_cache)
    for entry in log_entries:
        ip_info = ip_info_cache.get(entry.get(ip_key), {})
        entry.update(ip_info)

def export_frequency_counts(df: pd.DataFrame, columns: List[str], file_prefix=""):
    for col in columns:
        filename = f"{file_prefix}freq_{col}.csv"
        df[col].value_counts().sort_values(ascending=False).to_csv(filename)
        print(f"Created {filename}")

def export_key_value(df: pd.DataFrame, filter_key=None, filter_value=None, file_prefix=""):
    filename = f"{file_prefix}filtered_{filter_key}-{filter_value}.csv"
    df[df[filter_key] == filter_value].to_csv(filename)
    print(f"Created {filename}")

# ======================================== Cowrie Honeypot ========================================

FILE_PATH_COWRIE = "/Users/nicholassaw/Downloads/cowrie/var/log/cowrie/cowrie.json"

logs_cowrie = json_to_list(FILE_PATH_COWRIE)
ip_info_cache = load_ip_info_cache()

add_ip_info(logs_cowrie, ip_info_cache, ip_key="src_ip")
save_ip_info_cache(ip_info_cache)

df_cowrie = pd.DataFrame(logs_cowrie)

export_frequency_counts(df_cowrie, ["username", "password", "src_ip", "input"], file_prefix="cowrie-")

# Number of distinct IPs
unique_ips = get_unique_values("src_ip", logs_cowrie)
print(f"Number of distinct IPs: {len(unique_ips)}")

export_key_value(df_cowrie, "src_ip", "134.122.33.75", file_prefix="cowrie-")

# ======================================== SSH Honeypot ========================================

FILE_PATH_WEB_HP = "/Users/nicholassaw/Downloads/data/hp-ssh.log"

logs_ssh_hp = json_to_list(FILE_PATH_WEB_HP)

df_ssh_hp = pd.DataFrame(logs_ssh_hp)
df_ssh_hp = df_ssh_hp[~df_ssh_hp['is_flask'].notna()]
df_ssh_hp = df_ssh_hp[~df_ssh_hp['request_method'].notna()]
df_ssh_hp = df_ssh_hp.dropna(axis=1, how="all")

df_ssh_hp.to_csv("test2.csv")

export_frequency_counts(df_ssh_hp, ["client_ip", "event_type", "username", "password"], file_prefix="ssh_hp-")

# Number of distinct IPs
unique_ips_hp = get_unique_values("client_ip", logs_ssh_hp)
print(f"Number of distinct IPs: {len(unique_ips_hp)}")

# ======================================== WEB Honeypot ========================================

FILE_PATH_WEB_HP = "/Users/nicholassaw/Downloads/data/hp-ssh.log"

logs_web_hp = json_to_list(FILE_PATH_WEB_HP)

df_web_hp = pd.DataFrame(logs_web_hp)
df_web_hp = df_web_hp[df_web_hp['is_flask'].notna()]
df_web_hp = df_web_hp.dropna(axis=1, how="all")

df_web_hp.to_csv("test.csv")
