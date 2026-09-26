import warnings, csv, os, sys
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

from vsz_tools import vSZ_calls
SmartZone = vSZ_calls()

HOST = "192.168.81.100"
USERNAME = os.environ.get("SZ_USERNAME")
PASSWORD = os.environ.get("SZ_PASSWORD")
ZONE = 'Default Zone'

# Read-only: reports the WLAN Group each AP Group uses on each radio (2.4GHz, 5GHz, 6GHz)
# and whether it is set on the AP Group or inherited from the zone.
# Nothing is changed on the controller.

BANDS = ["2.4GHz", "5GHz", "6GHz"]


# Work out which radio a WLAN group setting belongs to from where it sits in the config
# (e.g. wlanGroup24, wlanGroup50, wlanGroup6g, radioConfig.radio6g.wlanGroup)
def bandOf(path):
	p = path.lower()
	if "24" in p or "2.4" in p or "2g" in p:
		return "2.4GHz"
	if "6g" in p or "6e" in p or "radio6" in p:
		return "6GHz"
	if "50" in p or "5g" in p or "radio5" in p:
		return "5GHz"
	return None


# Find every WLAN group setting in a zone / AP group config: {band: wlanGroupName}
def findWlanGroups(config, wlanGroupNames, path=""):
	found = {}
	if isinstance(config, dict):
		for key, value in config.items():
			keyPath = path + "." + key if path else key
			if "wlangroup" in key.lower() and not isinstance(value, (list, bool)):
				band = bandOf(keyPath)
				name = None
				if isinstance(value, dict):
					name = value.get("name") or wlanGroupNames.get(value.get("id"), value.get("id"))
				elif isinstance(value, str) and value:
					name = wlanGroupNames.get(value, value)
				if band and name and band not in found:
					found[band] = name
			elif isinstance(value, dict):
				for band, name in findWlanGroups(value, wlanGroupNames, keyPath).items():
					found.setdefault(band, name)
	return found


def main():
	if not USERNAME or not PASSWORD:
		sys.exit("Set SZ_USERNAME and SZ_PASSWORD environment variables first")
	token = None
	#Authenticate and get token:
	print("Authenticating to SmartZone")
	try:

		token = SmartZone.getToken(HOST, USERNAME, PASSWORD)
		zoneID = SmartZone.getZoneID(HOST, ZONE, token)

	except:

		print("Problem Connecting to SmartZone")

	if token != None:
		print("Got Zone: "+ZONE+" ID:"+zoneID)
		print(HOST)

		#WLAN Group ID -> Name, for configs that only return the ID
		wlanGroupNames = {}
		try:
			for group in SmartZone.getWlanGroupList(HOST, zoneID, token)["list"]:
				wlanGroupNames[group["id"]] = group["name"]
		except:
			pass

		rows = []
		zoneWlanGroups = findWlanGroups(SmartZone.queryZone(HOST, zoneID, token), wlanGroupNames)
		row = {"Level": "Zone", "Name": ZONE}
		for band in BANDS:
			row[band + " WLAN Group"] = zoneWlanGroups.get(band, "")
			row[band + " Set At"] = "Zone" if band in zoneWlanGroups else ""
		print(row)
		rows.append(row)

		apGroupList = SmartZone.getAPGroupList(HOST, zoneID, token)["list"]
		for group in sorted(apGroupList, key=lambda g: g["name"]):
			groupWlanGroups = findWlanGroups(SmartZone.getAPGroup(HOST, zoneID, group["id"], token), wlanGroupNames)
			row = {"Level": "AP Group", "Name": group["name"]}
			for band in BANDS:
				if band in groupWlanGroups:
					row[band + " WLAN Group"] = groupWlanGroups[band]
					row[band + " Set At"] = "AP Group"
				elif band in zoneWlanGroups:
					row[band + " WLAN Group"] = zoneWlanGroups[band]
					row[band + " Set At"] = "Zone (inherited)"
				else:
					row[band + " WLAN Group"] = ""
					row[band + " Set At"] = ""
			print(row)
			rows.append(row)

		fields = ["Level", "Name"]
		for band in BANDS:
			fields = fields + [band + " WLAN Group", band + " Set At"]
		with open('apgroup_wlan_groups.csv', 'w', newline='') as f:
			writer = csv.DictWriter(f, fieldnames=fields, restval="")
			writer.writeheader()
			writer.writerows(rows)
		print("Wrote " + str(len(rows)) + " rows to apgroup_wlan_groups.csv")

if __name__ == "__main__":
	main()
