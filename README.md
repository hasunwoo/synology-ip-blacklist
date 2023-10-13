# Synology IP Blacklist
Python scripts that automatically updates IP blacklists of synology nas from [blocklist.de](https://www.blocklist.de) and [abuseipdb.com](https://www.abuseipdb.com).

This script will help you to prevent brute force attacks from bad IPs.

# Setup Instructions
1. Get your own AbuseIPDB API key.
2. Put yout AbuseIPBD API key in [line 7](ip_blacklist_update.py#7).
3. Save updated [ip_blacklist_update.py](ip_blacklist_update.py) in your synology nas. It is recommended to save it to shared folder which won't be removed after update.
4. Create task schedular Job to run it periodically.

# Example Task Scheduler Job Configuration

## General Settings
**Task:** Update IP Blacklist

**User:** root

## Schedule

**Date:** Repeat Daily

**Time:** Continue running within the same dat

**Repeat:** Every 12 hours

## Schedule

**Run command:** `sudo python /volume1/system/ip_blacklist_update.py`



