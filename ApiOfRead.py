# -*- coding: UTF-8 -*-
import os
import requests as req
import json,sys,time,random

app_num=os.getenv('APP_NUM')
if app_num == '':
    app_num = '1'
access_token_list=['wangziyingwen']*int(app_num)
###########################
# config Option Description
# 0：off,  ， 1：on
# api_rand：Whether to sort apis randomly (12 random selections are enabled, 10 are disabled by default). Default 1 is on
# rounds: The number of rounds, that is, how many rounds are run each time it is started.
# rounds_delay: Whether to enable random delay between rounds, the last two parameters represent the delay interval. Default 0 off
# api_delay: Whether to enable the delay between APIs, the default is 0 to disable
# app_delay: Whether to enable the delay between accounts, the default is 0 to disable
########################################
config = {
         'api_rand': 1,
         'rounds': 3,
         'rounds_delay': [0,60,120],
         'api_delay': [0,2,6],
         'app_delay': [0,30,60],
         }
api_list = [
           r'https://graph.microsoft.com/v1.0/me/',
           r'https://graph.microsoft.com/v1.0/users',
           r'https://graph.microsoft.com/v1.0/me/people',
           r'https://graph.microsoft.com/v1.0/groups',
           r'https://graph.microsoft.com/v1.0/me/contacts',
           r'https://graph.microsoft.com/v1.0/me/drive/root',
           r'https://graph.microsoft.com/v1.0/me/drive/root/children',
           r'https://graph.microsoft.com/v1.0/drive/root',
           r'https://graph.microsoft.com/v1.0/me/drive',
           r'https://graph.microsoft.com/v1.0/me/drive/recent',
           r'https://graph.microsoft.com/v1.0/me/drive/sharedWithMe',
           r'https://graph.microsoft.com/v1.0/me/calendars',
           r'https://graph.microsoft.com/v1.0/me/events',
           r'https://graph.microsoft.com/v1.0/sites/root',
           r'https://graph.microsoft.com/v1.0/sites/root/sites',
           r'https://graph.microsoft.com/v1.0/sites/root/drives',
           r'https://graph.microsoft.com/v1.0/sites/root/columns',
           r'https://graph.microsoft.com/v1.0/me/onenote/notebooks',
           r'https://graph.microsoft.com/v1.0/me/onenote/sections',
           r'https://graph.microsoft.com/v1.0/me/onenote/pages',
           r'https://graph.microsoft.com/v1.0/me/messages',
           r'https://graph.microsoft.com/v1.0/me/mailFolders',
           r'https://graph.microsoft.com/v1.0/me/outlook/masterCategories',
           r'https://graph.microsoft.com/v1.0/me/mailFolders/Inbox/messages/delta',
           r'https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messageRules',
           r"https://graph.microsoft.com/v1.0/me/messages?$filter=importance eq 'high'",
           r'https://graph.microsoft.com/v1.0/me/messages?$search="hello world"',
           r'https://graph.microsoft.com/beta/me/messages?$select=internetMessageHeaders&$top',
           ]

#Microsoft refresh_token acquisition
def getmstoken(ms_token,appnum):
    headers={'Content-Type':'application/x-www-form-urlencoded'
            }
    data={'grant_type': 'refresh_token',
        'refresh_token': ms_token,
        'client_id':client_id,
        'client_secret':client_secret,
        'redirect_uri':'http://localhost:53682/'
        }
    html = req.post('https://login.microsoftonline.com/common/oauth2/v2.0/token',data=data,headers=headers)
    jsontxt = json.loads(html.text)
    if 'refresh_token' in jsontxt:
        print(r'The Microsoft key for the account/app '+str(appnum)+' was obtained successfully')
    else:
        print(r'The Microsoft key for the account/app '+str(appnum)+' Failed to obtain'+'\n'+'Please check whether the format and content of CLIENT_ID , CLIENT_SECRET , MS_TOKEN in secret are correct, and then reset')
    refresh_token = jsontxt['refresh_token']
    access_token = jsontxt['access_token']
    return access_token

#call function
def runapi(apilist,a):
    localtime = time.asctime( time.localtime(time.time()) )
    access_token=access_token_list[a-1]
    headers={
            'Authorization': 'bearer ' + access_token,
            'Content-Type': 'application/json'
            }
    for b in range(len(apilist)):	
        if req.get(api_list[apilist[b]],headers=headers).status_code == 200:
            print('The api call of No. '+str(apilist[b])+" succeeded")
        else:
            print("pass")
        if config['api_delay'][0] == 1:
            time.sleep(random.randint(config['api_delay'][1],config['api_delay'][2]))

#Obtain access_token at one time to reduce the acquisition rate
for a in range(1, int(app_num)+1):
    client_id=os.getenv('CLIENT_ID_'+str(a))
    client_secret=os.getenv('CLIENT_SECRET_'+str(a))
    ms_token=os.getenv('MS_TOKEN_'+str(a))
    access_token_list[a-1]=getmstoken(ms_token,a)

#random api sequence
fixed_api=[0,1,5,6,20,21]
#Guaranteed to extract the api of outlook and onedrive
ex_api=[2,3,4,7,8,9,10,22,23,24,25,26,27,13,14,15,16,17,18,19,11,12]
#Additional extraction and filling api
fixed_api.extend(random.sample(ex_api,6))
random.shuffle(fixed_api)
final_list=fixed_api

#Actual operation
if int(app_num) > 1:
    print('In multi-account/application mode, a bunch of *** may appear in the log report, which is normal')
print("If the number of APIs is less than the specified value, the API authorization has not been done properly, or the onedrive has not been initialized successfully. For the former, please re-authorize and obtain a Microsoft key replacement, for the latter, please wait a few days")
print('common '+str(app_num)+r' Account/App，'+r'per account/app '+str(config['rounds'])+' round') 
for r in range(1,config['rounds']+1):
    if config['rounds_delay'][0] == 1:
        time.sleep(random.randint(config['rounds_delay'][1],config['rounds_delay'][2]))		
    for a in range(1, int(app_num)+1):
        if config['app_delay'][0] == 1:
            time.sleep(random.randint(config['app_delay'][1],config['app_delay'][2]))
        client_id=os.getenv('CLIENT_ID_'+str(a))
        client_secret=os.getenv('CLIENT_SECRET_'+str(a))
        print('\n'+'App/Account '+str(a)+' First'+str(r)+'round '+time.asctime(time.localtime(time.time()))+'\n')
        if config['api_rand'] == 1:
            print("Random order has been turned on, a total of 12 apis, their own number")
            apilist=final_list
        else:
            print("The original order, a total of ten APIs, count by yourself")
            apilist=[5,9,8,1,20,24,23,6,21,22]
        runapi(apilist,a)
