import warnings, csv, re, os, sys
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

from vsz_tools import vSZ_calls
SmartZone = vSZ_calls()

HOST = "203.46.75.167"
USERNAME = os.environ.get("SZ_USERNAME")
PASSWORD = os.environ.get("SZ_PASSWORD")
ZONE = 'Paul-Test'


# Cache of AP Group names per zone: {zoneId: {apGroupId: apGroupName}}
apGroupNames = {}

# Look up an AP Group's name from its ID (group list is fetched once per zone)
def getAPGroupName(zoneId, apGroupId, token):
	if zoneId == None or apGroupId == None:
		return None
	if zoneId not in apGroupNames:
		apGroupNames[zoneId] = {}
		try:
			for group in SmartZone.getAPGroupList(HOST,zoneId,token)["list"]:
				apGroupNames[zoneId][group["id"]] = group["name"]
		except:
			pass
	return apGroupNames[zoneId].get(apGroupId)

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
		apList = SmartZone.queryAPs(HOST,"","",5000,token)
		rows = []
		portNames = set()
		for ap in apList:
			thisAPconfig = SmartZone.getAP(HOST,ap["apMac"],token)
			zoneId = thisAPconfig.get("zoneId", ap.get("zoneId"))
			apGroupId = thisAPconfig.get("apGroupId", ap.get("apGroupId"))
			apGroup = getAPGroupName(zoneId, apGroupId, token) or ap.get("apGroupName") or "Unknown AP Group"
			row = {"AP MAC": ap["apMac"], "AP Group": apGroup}
			try:
				ports = {}
				for port in thisAPconfig["specific"]["lanPorts"]:
					ports[port["portName"]] = port["ethPortProfile"]["name"]
				row.update(ports)
				portNames.update(ports)
				row["AP Level Port Config"] = "Yes"
			except:
				row["AP Level Port Config"] = "No"
			print(row)
			rows.append(row)

		#One column per LAN port seen on any AP, in natural order (LAN1, LAN2, ... LAN10)
		portColumns = sorted(portNames, key=lambda p: (re.sub(r"\d+", "", p), int(re.sub(r"\D", "", p) or 0)))
		with open('output.csv', 'w', newline='') as f:
			writer = csv.DictWriter(f, fieldnames=["AP MAC", "AP Group", "AP Level Port Config"] + portColumns, restval="")
			writer.writeheader()
			writer.writerows(rows)
		print("Wrote " + str(len(rows)) + " APs to output.csv")
			
if __name__ == "__main__":
	main()
