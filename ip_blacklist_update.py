from urllib import request
from ipaddress import ip_address, IPv4Address, IPv6Address
import sqlite3
import time

ABUSE_KEY = "<YOUR_ABUSE_KEY>"
SQLITE_DB = "/etc/synoautoblock.db"

def download_blocklist():
    resp = request.urlopen("https://lists.blocklist.de/lists/all.txt")
    data = resp.read()
    return data.decode("utf-8").split("\n")

def download_abuseipdb(key):
    headers = {
        "key": key,
        "Accept": "text/plain",
    }
    req_query = "confidenceMinimum=25"
    req = request.Request("https://api.abuseipdb.com/api/v2/blacklist?" + req_query, headers=headers)
    resp = request.urlopen(req)
    resp_data = resp.read()
    return resp_data.decode("utf-8").split("\n")

def prepare_ip_list(ip_list):
    result = []
    failed = 0
    for ip in ip_list:
        try:
            ip = ip_address(ip)
            if type(ip) is not IPv4Address:
                continue
            if ip.is_link_local or ip.is_private:
                continue 
            result.append((ip, ipv4_mapped_ipv6(ip)))
        except ValueError:
            failed += 1
    return (result, failed)

def ipv4_mapped_ipv6(ipv4):
    if type(ipv4) is not IPv4Address: 
        return None
    return IPv6Address(f"0:0:0:0:0:FFFF:{ipv4}")

ip_blacklist = set()

print("Downloading blacklist from blocklist.de...")
blocklist_blacklist = download_blocklist()
print(f"blocklist.de: Successfully downloaded {len(blocklist_blacklist)} IPs.")
ip_blacklist.update(blocklist_blacklist)

print("Downloading blacklist from abuseipdb.com...")
abuseipdb_blacklist = download_abuseipdb(ABUSE_KEY)
print(f"abuseipdb.com: Successfully downloaded {len(abuseipdb_blacklist)} IPs.")
ip_blacklist.update(abuseipdb_blacklist)

print(f"Blacklist total: {len(ip_blacklist)}")

print("Parsing ip addresses and filtering out valid ipv4 address...")
ip_blacklist, parse_failed = prepare_ip_list(ip_blacklist)
print(f"Parsing failed: {parse_failed}")
print(f"Total entries after filtering: {len(ip_blacklist)}")

unix_timestamp = int(time.time())
commit_data = map(lambda ip: (str(ip[0]), unix_timestamp, ip[1].exploded.upper()), ip_blacklist)

print(f"Connecting to SQLite DB: {SQLITE_DB}")
db = sqlite3.connect(SQLITE_DB)
cursor = db.cursor()

print("Removing existing entries...")
cursor.execute("delete from AutoBlockIP")

print("Adding new entries...")
# AutoBlockIP VALUES(IP, RecordTime, ExpireTime, Deny, IPStd(ipv6 mapped), Type, Meta)
cursor.executemany("insert into AutoBlockIP VALUES(?, ?, 0, 1, ?, 0, '')", commit_data)

print("Commiting...")
db.commit()

print("Closing...")
db.close()