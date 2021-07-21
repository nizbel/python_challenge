
def is_valid_ip(ip):
    parts = ip.split('.')
    parts = list(filter(lambda part: int(part) <= 255, parts))
    return len(parts) == 4