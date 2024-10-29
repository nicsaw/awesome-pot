import json, requests
import pandas as pd
from typing import List, Dict, Set, Any

class Analyser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.logs: List[Dict[str, Any]] = self.json_to_list(file_path)
        # self.add_ip_info(self.logs)
        self.df: pd.DataFrame = pd.DataFrame(self.logs)

    def json_to_list(self, file_path: str) -> List[Dict[str, Any]]:
        log_entries = []
        try:
            with open(file_path, 'r') as log_file:
                for line in log_file:
                    log_entry = json.loads(line)
                    log_entries.append(log_entry)
        except Exception as e:
            print(e)
        return log_entries

    def get_all_keys(self, log_entries) -> Set[str]:
        return {key for entry in log_entries for key in entry.keys()}

    def filter(self, log_entries=None, filter_key=None, filter_value=None) -> List[Dict[str, Any]]:
        log_entries = log_entries or self.logs
        if filter_key and filter_value == None:
            return [entry for entry in log_entries if filter_key in entry]
        return [entry for entry in log_entries if entry.get(filter_key) == filter_value]

    def get_values(self, key, log_entries=None) -> List[Any]:
        log_entries = log_entries or self.logs
        return [entry[key] for entry in log_entries if key in entry]

    def get_unique_values(self, key: str, log_entries=None) -> Set[Any]:
        log_entries = log_entries or self.logs
        return set(self.get_values(key, log_entries))

    def get_ip_info(self, ip: str):
        try:
            response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
            data = response.json()
            data.pop("ip", None)
            data.pop("readme", None)

            return data
        except Exception as e:
            print(f"ERROR get_ip_info({ip}): {e}")

    def add_ip_info(self, log_entries=None):
        log_entries = log_entries or self.logs
        unique_ips = self.get_unique_values("src_ip", log_entries=None)
        ip_info_mapping = {ip: self.get_ip_info(ip) for ip in unique_ips}

        for entry in log_entries:
            ip_info = ip_info_mapping.get(entry["src_ip"], {})
            entry.update(ip_info)

    def export_frequency_counts(self, columns: List[str]):
        for col in columns:
            filename = f"cowrie_freq_{col}.csv"
            self.df[col].value_counts().sort_values(ascending=False).to_csv(filename)
            print(f"Created {filename}")

    def export_key_value(self, filter_key=None, filter_value=None) -> List[Dict[str, Any]]:
        self.df[self.df[filter_key] == filter_value].to_csv(f"cowrie_{filter_key}-{filter_value}.csv")

FILE_PATH = "/Users/nicholassaw/Downloads/cowrie/var/log/cowrie/cowrie.json"
analyser = Analyser(FILE_PATH)

analyser.export_frequency_counts(["username", "password", "src_ip", "input"])

# Number of distinct IPs
print(f"Number of distinct IPs: {len(set(analyser.get_values("src_ip")))}")

analyser.export_key_value("src_ip", "134.122.33.75")
