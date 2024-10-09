import logging, datetime, json

def log(level="info", **kwargs):
    log_entry = {
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        "client_ip": kwargs.get('client_ip', None),
        "event_type": kwargs.get('event_type', 'generic_event'),
    }

    extra_fields = {k: v for k, v in kwargs.items() if k not in log_entry}
    log_entry.update(extra_fields)

    if level.lower() == "info":
        logging.info(json.dumps(log_entry))
    elif level.lower() == "warning":
        logging.warning(json.dumps(log_entry))
    elif level.lower() == "error":
        logging.error(json.dumps(log_entry))
    elif level.lower() == "critical":
        logging.critical(json.dumps(log_entry))
    elif level.lower() == "debug":
        logging.debug(json.dumps(log_entry))
