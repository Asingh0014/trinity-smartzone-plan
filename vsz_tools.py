import requests

class vSZ_calls:
	# Get authentication token
	def getToken(self, host, username, password):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/serviceTicket"
		body = {'username': username,'password': password}
		r = requests.post(url, json = body, verify=False)
		token = r.json()['serviceTicket']
		return token

	
	# Get zoneID (uses pagination)
	def getZoneID(self, host, zone, token):
		listSize = 1000
		index = 0
		hasMore = True
		zoneList = []
		while hasMore == True:
			url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/rkszones?listSize=" + str(listSize) + "&index=" + str(index) + "&serviceTicket=" + token
			r = requests.get(url, verify=False).json()
			zoneList = zoneList + r['list']
			if r['hasMore'] ==  False:
				hasMore = False
			index = index + listSize
		for item in zoneList:
			if item['name'] == zone:
				zoneID = item['id']
				return zoneID

	# Query zone
	def queryZone(self, host, zoneID, token):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/rkszones/" + zoneID + "?serviceTicket=" + token
		r = requests.get(url, verify=False)
		#print (r)
		return r.json()

# Add AP to AP Group
	def addAPtoAPGroup(self, host, zoneID, apGroupID, apMAC, token):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/rkszones/" + zoneID + "/apgroups/" + apGroupID + "/members/" + apMAC+ "?serviceTicket=" + token
		body = {}
		r = requests.post(url, json = body, verify=False)
		return r


	# Query APs (uses pagination)
	def queryAPs(self, host, filter, ID, limit, token):
		page = 1
		hasMore = True
		apList = []
		while hasMore == True:
			url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/query/ap?serviceTicket=" + token
			body = {
					"filters": [
					],
					"sortInfo": {
					"sortColumn": "apMac",
					"dir": "ASC"
					},
					"page": page,
					"limit": limit
					}
			r = requests.post(url, json = body, verify=False).json()
			apList = apList + r['list']
			if r['hasMore'] ==  False:
				hasMore = False
			page = page + 1
		return apList

	# Move AP to new cluster
	def moveAPtoNewCluster(self, host, newCluster, apList, deleteRecord, token):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/aps/switchoverCluster?serviceTicket=" + token
		body = {"ipOrFqdn":newCluster,"apMacList":apList,"deleteRecord":deleteRecord}
		r = requests.post(url, json = body, verify=False)	
		return r

	# Move AP to zone
	def moveAPtoZone(self, host, APmac, zoneId, token):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/aps/move?serviceTicket=" + token
		body = {
    			"targetZoneId": zoneId,
    			"apMacs": APmac
				}	
		r = requests.post(url, json = body, verify=False)	
		return r

	# Create access point
	def createAP(self, host, mac, zoneId, name, token):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/aps?serviceTicket=" + token
		body = {
				"mac": mac,
				"zoneId": zoneId,
				"name": name
				}
		
		r = requests.post(url, json = body, verify=False)	
		return r

	# Delete access point
	def deleteAP(self, host, mac, token):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/aps/" + mac + "?serviceTicket=" + token
		r = requests.delete(url, verify=False)	
		return r

	# Get access point configuration
	def getAP(self, host, mac, token):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/aps/" + mac + "?serviceTicket=" + token
		r = requests.get(url, verify=False)	
		return r.json()

	def getAPGroupList(self, host, zoneID, token):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/rkszones/" + zoneID + "/apgroups?listSize=500&serviceTicket=" + token
		r = requests.get(url, verify=False)

		return r.json()

	# Get zone level model specific config (e.g. model = "H510")
	def getZoneAPModel(self, host, zoneID, model, token):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/rkszones/" + zoneID + "/apmodel/" + model + "?serviceTicket=" + token
		r = requests.get(url, verify=False)
		return r

	# Get AP group model specific override (empty if the group uses the zone config)
	def getAPGroupAPModel(self, host, zoneID, apGroupID, model, token):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/rkszones/" + zoneID + "/apgroups/" + apGroupID + "/apmodel/" + model + "?serviceTicket=" + token
		r = requests.get(url, verify=False)
		return r

	# Remove AP group model specific override (group falls back to the zone config)
	def deleteAPGroupAPModel(self, host, zoneID, apGroupID, model, token):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/rkszones/" + zoneID + "/apgroups/" + apGroupID + "/apmodel/" + model + "?serviceTicket=" + token
		r = requests.delete(url, verify=False)
		return r

	# Remove AP level model specific override (AP falls back to its AP group / zone config)
	def deleteAPSpecific(self, host, mac, token):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/aps/" + mac + "/specific?serviceTicket=" + token
		r = requests.delete(url, verify=False)
		return r
            
	# Create client traffic by Wlan (uses pagination)
	def getTrafficByWlan(self, host, zoneId, wlanName, limit, token):
		page = 1
		hasMore = True
		clientList = []
		while hasMore == True:
			url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/clients/byWlanName/" + wlanName + "?serviceTicket=" + token
			body = {
					"filters": [
						{
						"type": "ZONE",
						"value": zoneId
						}
					],
					"page": page,
					"limit": limit
					}
			r = requests.post(url, json = body, verify=False).json()
			clientList = clientList + r['list']
			if r['hasMore'] ==  False:
				hasMore = False
			page = page + 1
		return clientList

	# Get Wireless clients (uses pagination)
	def getClients(self, host, zoneId, limit, token):
		page = 1
		hasMore = True
		clientList = []
		while hasMore == True:
			url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/query/client?serviceTicket=" + token
			body = {
					"filters": [
						{
						"type": "ZONE",
						"value": zoneId
						}
					],
					"page": page,
					"limit": limit
					}
			r = requests.post(url, json = body, verify=False).json()
			clientList = clientList + r['list']
			if r['hasMore'] ==  False:
				hasMore = False
			page = page + 1
		return clientList

	# Get DPSKs
	def getDPSKs(self, host, zoneId, wlanId, token):
		url = "https://" + host + ":8443" + "/wsg/api/public/v11_0/rkszones/" + zoneId + "/wlans/" + wlanId + "/dpsk?serviceTicket=" + token
		r = requests.get(url, verify=False)	
		return r.json()
