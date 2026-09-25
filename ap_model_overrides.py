import warnings, csv, re, os, sys, argparse
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

from vsz_tools import vSZ_calls
SmartZone = vSZ_calls()

HOST = "192.168.81.100"
USERNAME = os.environ.get("SZ_USERNAME")
PASSWORD = os.environ.get("SZ_PASSWORD")
ZONE = 'Default Zone'

# AP models to check, and the Ethernet port profile the zone should give LAN1-4
MODELS = ["H510", "H550"]
TARGET_PROFILE = "Student Wired 2026"
TARGET_PORTS = ["LAN1", "LAN2", "LAN3", "LAN4"]

OUTFILE = "model_overrides.csv"


# Turn a model specific config into {portName: profile name}
def portSummary(config):
	ports = {}
	for port in (config or {}).get("lanPorts") or []:
		if port.get("enabled", True) == False:
			ports[port.get("portName")] = "Disabled"
		else:
			ports[port.get("portName")] = (port.get("ethPortProfile") or {}).get("name", "")
	return ports

# Read an AP group's model override. Returns (state, config): state is "Yes", "No" or "Error HTTP xxx"
def groupOverride(zoneID, groupID, model, token):
	r = SmartZone.getAPGroupAPModel(HOST, zoneID, groupID, model, token)
	if r.status_code == 204 or (r.status_code == 200 and r.text.strip() in ("", "{}")):
		return "No", {}
	if r.status_code == 200:
		return "Yes", r.json()
	return "Error HTTP " + str(r.status_code), {}


def main():
	parser = argparse.ArgumentParser(description="Report (and optionally remove) AP group and AP level model specific overrides for " + "/".join(MODELS))
	parser.add_argument("--remove", action="store_true", help="remove the overrides found (asks for confirmation)")
	parser.add_argument("--groups", nargs="+", metavar="GROUP", help="only remove overrides in these AP groups (default: all groups)")
	args = parser.parse_args()

	if not USERNAME or not PASSWORD:
		sys.exit("Set SZ_USERNAME and SZ_PASSWORD environment variables first")

	print("Authenticating to SmartZone")
	try:
		token = SmartZone.getToken(HOST, USERNAME, PASSWORD)
		zoneID = SmartZone.getZoneID(HOST, ZONE, token)
	except:
		sys.exit("Problem Connecting to SmartZone")
	print("Got Zone: " + ZONE + " ID:" + zoneID)

	rows = []

	#Zone level (the config everything falls back to)
	zoneReady = True
	for model in MODELS:
		r = SmartZone.getZoneAPModel(HOST, zoneID, model, token)
		ports = portSummary(r.json()) if r.status_code == 200 and r.text.strip() else {}
		if any(ports.get(p) != TARGET_PROFILE for p in TARGET_PORTS):
			zoneReady = False
		rows.append(dict({"Level": "Zone", "Name": ZONE, "AP Group": "", "Model": model, "Override": "n/a"}, **ports))
		print("Zone " + model + ": " + str(ports))

	#AP group level
	groups = SmartZone.getAPGroupList(HOST, zoneID, token)["list"]
	groupNames = {}
	groupTargets = []
	for group in groups:
		groupNames[group["id"]] = group["name"]
		for model in MODELS:
			state, config = groupOverride(zoneID, group["id"], model, token)
			rows.append(dict({"Level": "AP Group", "Name": group["name"], "AP Group": group["name"], "Model": model, "Override": state}, **portSummary(config)))
			if state == "Yes":
				groupTargets.append((group, model))
				print("AP Group override: " + group["name"] + " / " + model + " " + str(portSummary(config)))
			elif state != "No":
				print("Could not read " + group["name"] + " / " + model + ": " + state)

	#AP level
	apTargets = []
	for ap in SmartZone.queryAPs(HOST, "", "", 5000, token):
		if ap.get("model") and ap["model"] not in MODELS:
			continue
		thisAPconfig = SmartZone.getAP(HOST, ap["apMac"], token)
		if thisAPconfig.get("model") not in MODELS:
			continue
		apGroup = groupNames.get(thisAPconfig.get("apGroupId"), thisAPconfig.get("apGroupId", ""))
		if thisAPconfig.get("specific"):
			apTargets.append((ap["apMac"], thisAPconfig, apGroup))
			ports = portSummary(thisAPconfig["specific"])
			rows.append(dict({"Level": "AP", "Name": ap["apMac"] + " " + thisAPconfig.get("name", ""), "AP Group": apGroup, "Model": thisAPconfig["model"], "Override": "Yes"}, **ports))
			print("AP override: " + ap["apMac"] + " " + thisAPconfig.get("name", "") + " (" + apGroup + ") " + str(ports))

	#Write report
	portNames = set()
	for row in rows:
		portNames.update(k for k in row if k.startswith("LAN"))
	portColumns = sorted(portNames, key=lambda p: int(re.sub(r"\D", "", p) or 0))
	with open(OUTFILE, 'w', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=["Level", "Name", "AP Group", "Model", "Override"] + portColumns, restval="")
		writer.writeheader()
		writer.writerows(rows)
	print("")
	print("Wrote " + OUTFILE + ": " + str(len(groupTargets)) + " AP group overrides, " + str(len(apTargets)) + " AP level overrides")

	if not args.remove:
		return

	#Removal
	if args.groups:
		groupTargets = [t for t in groupTargets if t[0]["name"] in args.groups]
		apTargets = [t for t in apTargets if t[2] in args.groups]
	if not groupTargets and not apTargets:
		print("Nothing to remove")
		return

	print("")
	print("About to REMOVE these overrides (ALL model specific settings, not just ports):")
	for group, model in groupTargets:
		print("  AP Group " + group["name"] + " / " + model)
	for mac, config, apGroup in apTargets:
		print("  AP " + mac + " " + config.get("name", "") + " (" + apGroup + ")")
	if not zoneReady:
		print("")
		print("WARNING: the zone " + "/".join(MODELS) + " config does not have " + TARGET_PROFILE + " on " + ",".join(TARGET_PORTS) + ".")
		print("These APs will fall back to the zone config above. Set the zone first.")
	if input("Type yes to continue: ").strip().lower() != "yes":
		print("Cancelled")
		return

	for group, model in groupTargets:
		r = SmartZone.deleteAPGroupAPModel(HOST, zoneID, group["id"], model, token)
		state, config = groupOverride(zoneID, group["id"], model, token)
		print("AP Group " + group["name"] + " / " + model + ": HTTP " + str(r.status_code) + (" - removed" if state == "No" else " - STILL OVERRIDDEN (" + state + ")"))
	for mac, config, apGroup in apTargets:
		r = SmartZone.deleteAPSpecific(HOST, mac, token)
		removed = not SmartZone.getAP(HOST, mac, token).get("specific")
		print("AP " + mac + ": HTTP " + str(r.status_code) + (" - removed" if removed else " - STILL OVERRIDDEN"))

if __name__ == "__main__":
	main()
