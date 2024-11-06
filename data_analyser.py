import json
import requests
import re
import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Set, Any

CACHE_FILENAME = "ip_info_cache.json"
FLASK_LOG_PATTERN = re.compile(r'(?P<client_ip>(\d{1,3}\.){3}\d{1,3}) - - \[(?P<timestamp>.*?)\] (?P<message>.*)')
IP_INFO_API_KEY = os.environ.get("IP_INFO_API_KEY")

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
            "client_ip": match.group("client_ip"),
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

def get_values(key: str, logs) -> List[Any]:
    return [entry[key] for entry in logs if key in entry]

def get_unique_values(key: str, logs) -> Set[Any]:
    return set(entry[key] for entry in logs if key in entry)

def load_ip_info_cache(cache_filename: str = CACHE_FILENAME) -> Dict[str, Any]:
    try:
        with open(cache_filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR loading cache: {e}")

def save_ip_info_cache(ip_info_cache: Dict[str, Any], cache_filename: str = CACHE_FILENAME) -> None:
    try:
        merged_cache = {**load_ip_info_cache(cache_filename), **ip_info_cache}
        with open(cache_filename, 'w') as f:
            json.dump(merged_cache, f, indent=4)
    except Exception as e:
        print(f"ERROR saving cache: {e}")

def is_valid_ip_info(ip: str, cache_filename: str = CACHE_FILENAME) -> bool:
    ip_info_cache = load_ip_info_cache(cache_filename)
    if ip not in ip_info_cache or ip_info_cache[ip].get("status") == 429:
        return False
    return True

def request_ip_info(ip: str, token=IP_INFO_API_KEY):
    try:
        if token:
            response = requests.get(f"https://ipinfo.io/{ip}/json?token={token}", timeout=5)
        else:
            response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        response.raise_for_status()
        data = response.json()
        data.pop("readme", None)
        return data
    except Exception as e:
        print(f"ERROR request_ip_info({ip}): {e}")
        return {}

def get_ip_info(ip_list: List[str], cache_filename: str = CACHE_FILENAME) -> Dict[str, Dict]:
    ip_info_cache = load_ip_info_cache(cache_filename)
    result = {}

    for ip in ip_list:
        if ip is None:
            print(f"{ip = }")
            continue
        if is_valid_ip_info(ip, cache_filename):
            result[ip] = ip_info_cache[ip]
        else:
            ip_info_cache[ip] = request_ip_info(ip)
            result[ip] = ip_info_cache[ip]

    save_ip_info_cache(ip_info_cache)
    return result

def get_ips_by_key_value(key: str, value: Any, cache_filename: str = CACHE_FILENAME) -> List[str]:
    return [ip for ip, info in load_ip_info_cache(cache_filename).items() if info.get(key) == value]

def clean_ip_info_cache(cache_filename: str = CACHE_FILENAME):
    ip_info_cache = load_ip_info_cache(cache_filename)
    rate_limited_ips = get_ips_by_key_value(key="status", value=429)
    for ip in rate_limited_ips:
        ip_info_cache[ip] = request_ip_info(ip)
    save_ip_info_cache(ip_info_cache)

def get_frequency_counts(df: pd.DataFrame, keys: List[str], file_prefix=""):
    for key in keys:
        if key in df.columns:
            filename = f"{file_prefix}freq_{key}.csv"
            df[key].value_counts().sort_values(ascending=False).to_csv(filename)
            print(f"Created {filename}")
        else:
            print(f"Column {key} not found in {df = }")

def get_frequency_counts(df: pd.DataFrame, keys: List[str], export: bool = True, file_prefix="") -> Dict[str, pd.DataFrame]:
    results = {}

    for key in keys:
        if key in df.columns:
            freq_counts = df[key].value_counts().sort_values(ascending=False)
            freq_counts_df = freq_counts.reset_index()
            results[key] = freq_counts_df

            if export:
                filename = f"{file_prefix}freq_{key}.csv"
                freq_counts_df.to_csv(filename)
                print(f"Created {filename}")
        else:
            print(f"Column {key} not found in {df = }")

    return results

def filter_by_key_value(df: pd.DataFrame, filter_key, filter_value, export: bool = True, file_prefix="") -> pd.DataFrame:
    filtered_df = df[df[filter_key] == filter_value]
    if export:
        filename = f"{file_prefix}filtered_{filter_key}-{filter_value}.csv"
        filtered_df.to_csv(filename)
        print(f"Created {filename}")
    return filtered_df

def get_unique_ip_info_df(logs: List[Dict[str, Any]], ip_key: str, cache_filename: str = CACHE_FILENAME) -> pd.DataFrame:
    unique_ips = get_unique_values(ip_key, logs)
    unique_ips_info = get_ip_info(list(unique_ips), cache_filename)
    return pd.DataFrame.from_dict(unique_ips_info, orient="index")

def plot_frequency_counts(frequency_counts: dict, top_n: int = 20, export: bool = True, file_prefix=""):
    for key, freq_df in frequency_counts.items():
        top_freq = freq_df.head(top_n).copy()

        total_count = top_freq["count"].sum()
        top_freq["percentage"] = (top_freq["count"] / total_count) * 100

        plt.figure(figsize=(10, 6))
        bars = plt.bar(top_freq[key], top_freq["count"], color="skyblue")

        for bar, percent in zip(bars, top_freq["percentage"]):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{percent:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9
            )

        plt.title(f"Top {top_n} Most Frequent Values for {key}")
        plt.xlabel(key.capitalize())
        plt.ylabel("Count")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        if export:
            filename = f"{file_prefix}top_{top_n}_{key}.png"
            plt.savefig(filename, format="png")
            print(f"Plotted {filename}")

        plt.show()

ip_info_cache = load_ip_info_cache()

print("============================== Cowrie Honeypot ==============================")

FILE_PREFIX_COWRIE = "c-"
FILE_PATH_COWRIE = "/Users/nicholassaw/Downloads/cowrie/var/log/cowrie/cowrie.json"
logs_cowrie = json_to_list(FILE_PATH_COWRIE)

df_cowrie = pd.DataFrame(logs_cowrie)
freq_counts = get_frequency_counts(df_cowrie, ["username", "password", "src_ip", "input"], file_prefix=FILE_PREFIX_COWRIE)
plot_frequency_counts(freq_counts, top_n=20, file_prefix=FILE_PREFIX_COWRIE)

df_cowrie_ip_info = get_unique_ip_info_df(logs_cowrie, ip_key="src_ip")
freq_counts_ip_info = get_frequency_counts(df_cowrie_ip_info, ["country"], file_prefix=FILE_PREFIX_COWRIE)
plot_frequency_counts(freq_counts_ip_info, top_n=20, file_prefix=FILE_PREFIX_COWRIE)

filter_by_key_value(df_cowrie, "src_ip", "159.223.123.14", file_prefix=FILE_PREFIX_COWRIE)

# Number of distinct IPs
unique_ips = get_unique_values("src_ip", logs_cowrie)
print(f"Number of distinct IPs: {len(unique_ips)}")

unique_username_password = df_cowrie.groupby(["username", "password"]).ngroups
print(f"Number of unique username-password combinations: {unique_username_password}")

print("============================== SSH Honeypot ==============================")

FILE_PREFIX_SSH_HP = "ssh_hp-"
FILE_PATH_SSH_HP = "/Users/nicholassaw/Downloads/data/hp-ssh.log"
logs_ssh_hp = json_to_list(FILE_PATH_SSH_HP)
logs_ssh_hp = [
    entry for entry in logs_ssh_hp
    if "is_flask" not in entry and "request_method" not in entry
]

df_ssh_hp = pd.DataFrame(logs_ssh_hp)
freq_counts = get_frequency_counts(df_ssh_hp, ["client_ip", "username", "password"], file_prefix=FILE_PREFIX_SSH_HP)
plot_frequency_counts(freq_counts, top_n=20, file_prefix=FILE_PREFIX_SSH_HP)

df_ssh_hp_ip_info = get_unique_ip_info_df(logs_ssh_hp, ip_key="client_ip")
freq_counts_ip_info = get_frequency_counts(df_ssh_hp_ip_info, ["country"], file_prefix=FILE_PREFIX_SSH_HP)
plot_frequency_counts(freq_counts_ip_info, top_n=20, file_prefix=FILE_PREFIX_SSH_HP)

# Number of distinct IPs
unique_ips_hp = get_unique_values("client_ip", logs_ssh_hp)
print(f"Number of distinct IPs: {len(unique_ips_hp)}")

unique_username_password = df_ssh_hp.groupby(["username", "password"]).ngroups
print(f"Number of unique username-password combinations: {unique_username_password}")

print("============================== Web Honeypot ==============================")

FILE_PREFIX_WEB_HP = "web_hp-"
FILE_PATH_WEB_HP = "/Users/nicholassaw/Downloads/data/hp-ssh.log"
logs_web_hp = json_to_list(FILE_PATH_WEB_HP)
logs_web_hp = [
    entry for entry in logs_web_hp
    if "is_flask" in entry or "request_method" in entry
]

df_web_hp = pd.DataFrame(logs_web_hp)
freq_counts = get_frequency_counts(df_web_hp, ["client_ip", "message"], file_prefix=FILE_PREFIX_WEB_HP)
plot_frequency_counts(freq_counts, top_n=20, file_prefix=FILE_PREFIX_WEB_HP)

df_web_hp_ip_info = get_unique_ip_info_df(logs_web_hp, ip_key="client_ip")
freq_counts_ip_info = get_frequency_counts(df_web_hp_ip_info, ["country"], file_prefix=FILE_PREFIX_WEB_HP)
plot_frequency_counts(freq_counts_ip_info, top_n=20, file_prefix=FILE_PREFIX_WEB_HP)

filter_by_key_value(df_web_hp, "client_ip", "90.151.171.106", file_prefix=FILE_PREFIX_WEB_HP)

# Number of distinct IPs
unique_ips_web_hp = get_unique_values("client_ip", logs_web_hp)
print(f"Number of distinct IPs: {len(unique_ips_web_hp)}")



clean_ip_info_cache()
save_ip_info_cache(ip_info_cache)
