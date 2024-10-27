import json, requests
import pandas as pd
from typing import List, Dict, Set, Any

def json_to_list(file_path: str) -> List[Dict[str, Any]]:
    log_entries = []
    try:
        with open(file_path, 'r') as log_file:
            for line in log_file:
                log_entry = json.loads(line)
                log_entries.append(log_entry)
    except Exception as e:
        print(e)
    return log_entries

def get_all_keys(log_entries) -> Set[str]:
    return {key for entry in log_entries for key in entry.keys()}

def filter(log_entries, filter_key=None, filter_value=None) -> List[Dict[str, Any]]:
    if filter_key and filter_value == None:
        return [entry for entry in log_entries if filter_key in entry]
    return [entry for entry in log_entries if entry.get(filter_key) == filter_value]

def get_values(log_entries, key):
    return [entry[key] for entry in log_entries if key in entry]

def get_ip_info(ip: str):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        data = response.json()
        data.pop("ip", None)
        data.pop("readme", None)

        return data
    except Exception as e:
        print(f"ERROR get_ip_info({ip}): {e}")

def add_ip_info(logs):
    unique_ips = {item["src_ip"] for item in logs}
    ip_info_mapping = {ip: get_ip_info(ip) for ip in unique_ips}

    for entry in logs:
        ip_info = ip_info_mapping.get(entry["src_ip"], {})
        entry.update(ip_info)

FILE_PATH = "/Users/nicholassaw/Downloads/cowrie/var/log/cowrie/cowrie.json"
logs: List[Dict[str, Any]] = json_to_list(FILE_PATH)
df = pd.read_json(FILE_PATH, lines=True)

# Number of distinct IPs
print(f"{len(set(get_values(logs, "src_ip")))}")

# Most common sernames
print(df["username"].value_counts().sort_values(ascending=False))

# Most common passwords
print(df["password"].value_counts().sort_values(ascending=False))

add_ip_info(logs)

df = pd.DataFrame(logs)

df.to_csv("cowrie_logs.csv", index=False)
