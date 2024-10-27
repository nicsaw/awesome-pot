import json
from typing import List, Dict, Set, Any

class Analyser:
    def __init__(self, file_path: str):
        self.logs: List[Dict[str, Any]] = self.json_to_list(file_path)

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

    def get_all_keys(self) -> Set[str]:
        return {key for entry in self.logs for key in entry.keys()}

    def filter(self, filter_key = None, filter_value = None) -> List[Dict[str, Any]]:
        if filter_key and filter_value == None:
            return [entry for entry in self.logs if filter_key in entry]
        return [entry for entry in self.logs if entry.get(filter_key) == filter_value]

    def get_values(self, key):
        return [entry[key] for entry in self.logs if key in entry]

FILE_PATH = "/Users/nicholassaw/Downloads/cowrie/var/log/cowrie/cowrie.json"
analyser = Analyser(FILE_PATH)

# Number of distinct IPs
print(len(set(analyser.get_values("src_ip"))))
