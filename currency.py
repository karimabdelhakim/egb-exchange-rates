import requests
from pymongo import MongoClient
from datetime import datetime
import json
import sys

#check if connection is on
def checkDbConnection():
	try:
		client = MongoClient(serverSelectionTimeoutMS=5000)
		client.server_info()
		return client
	except:
	    print('No mongodb found') 
	    sys.exit()

#create db if not exist
db = checkDbConnection().currencydb#client.currencydb
#create collection if not exist
collection = db.currency

#currency api
url = "http://free.currencyconverterapi.com/api/v3/convert"


#get currency(EGP) exchange rate from the api given another currency code
#param(currency):currency code
def currencyToEGP(currency):
	currency = currency.upper()
	q = "{curr}_EGP".format(curr=currency)
	querystring = {"q":q,"compact":"ultra"}
	response = requests.request("GET", url, params=querystring)
	resp_parsed = response.json()
	if response.status_code==200 and resp_parsed:
		rate = str(resp_parsed[q])
		insertIntoDb(currency,rate) 
		data = rate + ' EGP'
		return {'data':data,'ok':True}
	return {'error':'Error: Invalid Currency code','ok':False}

#start the cli
def start():
	user_input  = raw_input('Enter 1 to convert a currency to EGP , 2 to list your today entries or any key to quit: ')
	if(user_input=='1'):
		convertCurrency()	
	elif(user_input=='2'):
		findAll()

#prompt user to enter a currency code and print its exchange rate or error
def convertCurrency():
	while True:
		curr_input  = raw_input('Enter a Currency code or 1 to go back: ')
		if curr_input == '1':
			break
		res = currencyToEGP(curr_input)
		if res['ok']:
			print res['data']

		else:
			print res['error']	
	start()		

#insert user entry into db if the currency code has not been entered before in the same day
#param(currency_code):currency code
#param(rate):exchange rate for that currency
def insertIntoDb(currency_code,rate):

	dect = {
		'currency code':currency_code,
		'exchange rate':rate,
		'date':datetime.now().strftime("%Y-%m-%d")
	}
	query = collection.find_one({
		'currency code':currency_code,
		'date':datetime.today().strftime("%Y-%m-%d")
	})
	if not query:
		collection.insert_one(dect)

#get user entries for today
def findAll():
	query = collection.find({
		'date':datetime.today().strftime("%Y-%m-%d")
	},{
		'_id':False
	})
	for document in query: 
		print(json.dumps(document)) 

	start()	

start()			

