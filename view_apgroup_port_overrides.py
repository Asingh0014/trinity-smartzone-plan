import warnings, csv, re, os, sys
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

from vsz_tools import vSZ_calls
SmartZone = vSZ_calls()

HOST = "192.168.81.100"
USERNAME = os.environ.get("SZ_USERNAME")
PASSWORD = os.environ.get("SZ_PASSWORD")
ZONE = 'Default Zone'
MODELS = ["H510", "H550"]

# Read-only: reports which AP Groups override the zone's model specific port settings.
# Nothing is changed on the controller.


# Turn a model specific config response into {portName: ethPortProfileName}
def lanPorts(response):
	if response.status_code != 200:
		return None
	try:
		config = response.json()
	except:
		return None
	ports = {}
	for port in config.get("lanPorts") or []:
		profile = (port.get("ethPortProfile") or {}).get("name", "")
		if port.get("enabled") == False:
			profile = "Disabled"
		ports[port.get("portName")] = profile
	return ports or None


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
		rows = []
		portNames = set()

		#Zone level settings first, so groups can be compared against them
		zonePorts = {}
		for model in MODELS:
			response = SmartZone.getZoneModelConfig(HOST, zoneID, model, token)
			zonePorts[model] = lanPorts(response)
			row = {"Level": "Zone", "Name": ZONE, "Model": model, "HTTP Status": response.status_code,
				"Overrides Zone": "", "Same As Zone": ""}
			row.update(zonePorts[model] or {})
			portNames.update(zonePorts[model] or {})
			print(row)
			rows.append(row)

		apGroupList = SmartZone.getAPGroupList(HOST, zoneID, token)["list"]
		for group in sorted(apGroupList, key=lambda g: g["name"]):
			for model in MODELS:
				response = SmartZone.getAPGroupModelConfig(HOST, zoneID, group["id"], model, token)
				ports = lanPorts(response)
				row = {"Level": "AP Group", "Name": group["name"], "Model": model, "HTTP Status": response.status_code}
				if ports:
					row["Overrides Zone"] = "Yes"
					row["Same As Zone"] = "Yes" if ports == zonePorts[model] else "No"
					row.update(ports)
					portNames.update(ports)
				else:
					row["Overrides Zone"] = "No"
					row["Same As Zone"] = ""
				print(row)
				rows.append(row)

		#One column per LAN port, in natural order (LAN1, LAN2, ... LAN10)
		portColumns = sorted(portNames, key=lambda p: (re.sub(r"\d+", "", p), int(re.sub(r"\D", "", p) or 0)))
		with open('apgroup_port_overrides.csv', 'w', newline='') as f:
			writer = csv.DictWriter(f, fieldnames=["Level", "Name", "Model", "Overrides Zone", "Same As Zone"] + portColumns + ["HTTP Status"], restval="")
			writer.writeheader()
			writer.writerows(rows)
		print("Wrote " + str(len(rows)) + " rows to apgroup_port_overrides.csv")
			
if __name__ == "__main__":
	main()
