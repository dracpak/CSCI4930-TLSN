from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256
from Crypto.Util.number import *
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

with open("myRecord.txt") as file:
    lines = [line.rstrip() for line in file]

hashChain = None

for r in lines:
	if r[:6] == "Public":
		pass
	else:
		if hashChain == None:
			hashChain = r[10:]
		else:
			pass
print(type(hashChain))
    
    
	  


