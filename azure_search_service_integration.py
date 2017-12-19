import json
import requests
api_key='' #api key from your azure search service

def azure_search(search_query):

	azure_search_service_rest_end_point = " "+search_query  #azure_search_service_rest_end_point
	headerPayload = {'api-key':api_key,"Content-Type":"application/x-www-form-urlencoded"}
	aure_storage_end_point=' ' #azure search storage end point

	try:
		resp_str = requests.get(azure_search_service_rest_end_point, headers=headerPayload)
		#print(resp_str)
		#print(str(resp_str.status_code))
		#print(str(resp_str.headers))
		#print(str(resp_str.text))
		resp_dict = json.loads(resp_str.text)
		#print(resp_dict)
		#dict_attributes_name_value={}
		list_attributes_name=['metadata_storage_name']
		list_attributes_value=[]
		size_of_list=len(resp_dict.get('value'))
		print(size_of_list)
		if size_of_list>0:
			#restrict the number of recommendation to top 3 values
			if(size_of_list>3):
				size_of_list=3

			for i in range(size_of_list):
				for l in list_attributes_name:
					list_attributes_value.append(resp_dict.get('value')[i][l])
			#for l in list_attributes_name:
				#dict_attributes_name_value[l]=resp_dict.get('value')[0][l]	
			#print(dict_attributes_name_value)
			print(list_attributes_value)
			url_list=[]	
			for i in range(len(list_attributes_value)):
				url_list.append(aure_storage_end_point+list_attributes_value[i])
			#print(url_list)
			return url_list,list_attributes_value
		else:
		    return 0,0	
	except Exception as e:
		msg = "Error >> There is an exception in azure_search_service_integration class. >>>>" + str(e)
		print(msg)
		return 0,0

#azure_search('abhishek bisht')
