import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
import json
from Crypto.Hash import SHA256
from Crypto.Util.number import *

hcn1 = None
record = []
lor = []
O = []
salt = []
req = [["GET", "https://localhost:4443/index.html"], ["GET", "https://localhost:4443/certificate.pem"], ["GET", "https://localhost:4443/key.pem"]]

outputFile = []

for r in req:
	record.append(r)
	lor.append(len(r[0]+r[1]))
	O.append(0)
	salt.append(os.urandom(32))
	
	
	cipher = AES.new(salt[-1], AES.MODE_ECB) # yeah I know ECB mode is garbage but C() not only has to be deterministic but the result gets hashed anyway should we need to keep the record private so its fine
	c = cipher.encrypt(pad(str(record[-1]).encode(), 32))
	
	private = str(lor[-1])+str(O[-1])
	private = private.encode() + c
	private = SHA256.new(private).digest()
	
	output = {
		"public": {
			"text": r[0]+" "+r[1],
			"salt": salt[-1],
			"lor": lor[-1],
			"O": O[-1],
			},
		"private": hex(bytes_to_long(private))
	}
	outputFile.append(output)
	if hcn1 == None:
		hcn1 = private
	else:
		hcn1 = SHA256.new(str(private).encode() + str(hcn1).encode())
	
	
	response = requests.request(r[0], r[1], verify=False)
	record.append(response.text)
	O.append(1)
	lor.append(len(response.text))
	salt.append(os.urandom(32))
	
	
	cipher = AES.new(salt[-1], AES.MODE_ECB) # yeah I know ECB mode is garbage but C() not only has to be deterministic but the result gets hashed anyway should we need to keep the record private so its fine
	c = cipher.encrypt(pad(str(record[-1]).encode(), 32))
	
	private = str(lor[-1])+str(O[-1])
	private = private.encode() + c
	private = SHA256.new(private).digest()
	
	output = {
		"public" : {
			"text" : response.text,
			"salt" : salt[-1],
			"lor" : lor[-1],
			"O" : O[-1]
			},
		"private" : hex(bytes_to_long(private))
	}
	outputFile.append(output)
	
	hcn1 = SHA256.new(str(private).encode() + str(hcn1).encode()).digest()
	
response = requests.request("GET", "https://localhost:4443/index.html?getEvidence=true&hcn1="+hex(bytes_to_long(hcn1)), verify=False)
signed_hash = response.text

f = open("myRecord.txt", "w")
for r in outputFile:
	print(type(r))
	print(r)
	val = input("\nProtect Record? (y/n)\n")
	if val == "y":
		f.write("Private: " + str(r["private"]) + "\n")
	else:
		f.write("Public: " + str(r["public"]) + "\n")
f.write(str({"signed SHA" : response.text}) + "\n")
	
