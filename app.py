import os, sys
from flask import Flask, request
import json
import requests
from azure_search_service_integration import azure_search
import traceback

app = Flask(__name__)

PAGE_ACCESS_TOKEN = ""#put your facebook page token

@app.route('/', methods=['GET'])
def verify():
	# Webhook verification
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == " ": #put your webhook verfy token
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200   
    return "Hello world", 200

def get_messaging_text_sender_id_recipient_id_from_messenger(data):
	try:
		if data['object'] == 'page':
			for entry in data['entry']:
				for messaging_event in entry['messaging']:
					# IDs
					sender_id = messaging_event['sender']['id']
					recipient_id = messaging_event['recipient']['id']

					if messaging_event.get('message'):
						# Extracting text message
						if 'text' in messaging_event['message']:
							messaging_text = messaging_event['message']['text']
						else:
							messaging_text = 'no_text'	
						return messaging_text,sender_id,recipient_id									
	except Exception as ex:
		print ("get_messaging_text_sender_id_recipient_id_from_messenger exception "+str(ex))
		print("There is an exception from function " + str(traceback.extract_stack(None, 2)[0][2]))
								
def prepare_response_content_generic(sender_id,text):
	try:
		response_content = {
							"recipient":{
							"id": sender_id
										},
											"message": {
											"text": text	            
											}
							}
		return response_content
	except Exception as ex:
		print ("prepare_response_content_generic exception "+str(ex))
		print("There is an exception from function " + str(traceback.extract_stack(None, 2)[0][2]))						

def prepare_response_content_buttons(sender_id,text,url,title='View Document'):
	try:
			response_content = {
								"recipient": {
											"id": sender_id
											},
								"message":{
											"attachment":{
											"type":"template",
											"payload":{
											"template_type":"button",
											"text":text,
											"buttons":[
											{
											"type":"web_url",
											"url":url,
											"title":title
											}]}}}}
			return response_content
	except Exception as ex:
			print ("prepare_response_content_buttons exception "+str(ex))
			print("There is an exception from function " + str(traceback.extract_stack(None, 2)[0][2]))

def get_response_from_azure_serch_service_api(messaging_text):
	try:
		url_list,list_attributes_value= azure_search(messaging_text)
		return url_list,list_attributes_value
	except Exception as ex:
			print ("get_response_from_azure_serch_service_api exception "+str(ex))
			print("There is an exception from function " + str(traceback.extract_stack(None, 2)[0][2]))		

def send_response_to_messenger(response_content):
	try:
			headers = {"Content-Type": "application/json"}
			url = "https://graph.facebook.com/v2.6/me/messages?access_token=%s" % PAGE_ACCESS_TOKEN
			resp_str = requests.post(url, data=json.dumps(response_content), headers=headers)
			return resp_str
	except Exception as ex:
			print ("send_response_to_messenger exception "+str(ex))
			print("There is an exception from function " + str(traceback.extract_stack(None, 2)[0][2]))

@app.route('/', methods=['POST'])
def webhook():
	data = request.get_json()
	try:
		messaging_text,sender_id,recipient_id=get_messaging_text_sender_id_recipient_id_from_messenger(data)        
		url_list,list_attributes_value=get_response_from_azure_serch_service_api(messaging_text)
		if  url_list!=0:
				response_content=prepare_response_content_generic(sender_id,"Hi,I have found "+str(len(url_list))+" "+"document related to your query."+'\n'+"Please click below link to open the document.")
				resp_str=send_response_to_messenger(response_content)
				for i in range(len(url_list)):
					response_content=prepare_response_content_buttons(sender_id,list_attributes_value[i],url_list[i])
					resp_str=send_response_to_messenger(response_content)
		else:
				response_content=prepare_response_content_generic(sender_id,"Hi,I have no document related to your search.")
				resp_str=send_response_to_messenger(response_content)
	except Exception as ex:
    		print ("main class exp "+str(ex))
    		print("There is an exception from function " + str(traceback.extract_stack(None, 2)[0][2]))
	return "ok", 200

def log(message):
	print(message)
	sys.stdout.flush()

if __name__ == "__main__":
	app.run(debug=True)
