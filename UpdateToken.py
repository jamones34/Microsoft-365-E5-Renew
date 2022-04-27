# -*- coding: UTF-8 -*-
import requests as req
import json
import os
from base64 import b64encode
from nacl import encoding, public

app_num=os.getenv('APP_NUM')
if app_num == '':
    app_num='1'
gh_token=os.getenv('GH_TOKEN')
gh_repo=os.getenv('GH_REPO')
#ms_token=os.getenv('MS_TOKEN')
#client_id=os.getenv('CLIENT_ID')
#client_secret=os.getenv('CLIENT_SECRET')
Auth=r'token '+gh_token
geturl=r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/public-key'
#puturl=r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/MS_TOKEN'
key_id='wangziyingwen'

#Get public key
def getpublickey(Auth,geturl):
    headers={'Accept': 'application/vnd.github.v3+json','Authorization': Auth}
    html = req.get(geturl,headers=headers)
    jsontxt = json.loads(html.text)
    if 'key' in jsontxt:
        print("Public key obtained successfully")
    else:
        print("Failed to obtain the public key, please check whether the GH_TOKEN format and settings in the secret are correct")
    public_key = jsontxt['key']
    global key_id 
    key_id = jsontxt['key_id']
    return public_key

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
        print(r'Account/App '+str(appnum)+' The Microsoft key was obtained successfully')
    else:
        print(r'Account/App '+str(appnum)+' The Microsoft key acquisition failed'+'\n'+'Please check the secret CLIENT_ID , CLIENT_SECRET , MS_TOKEN Is the format and content correct, then reset')
    refresh_token = jsontxt['refresh_token']
    access_token = jsontxt['access_token']
    return refresh_token
#Do you want to save access，To reduce the refresh rate of Microsoft token???

#token encryption
def createsecret(public_key,secret_value):
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

#token upload
def setsecret(encrypted_value,key_id,puturl,appnum):
    headers={'Accept': 'application/vnd.github.v3+json','Authorization': Auth}
    #data={'encrypted_value': encrypted_value,'key_id': key_id}  ->400error
    data_str=r'{"encrypted_value":"'+encrypted_value+r'",'+r'"key_id":"'+key_id+r'"}'
    putstatus=req.put(puturl,headers=headers,data=data_str)
    if putstatus.status_code >= 300:
        print(r'Account/App '+str(appnum)+' Microsoft key upload failed，Please check if the GH_TOKEN format and settings in the secret are correct')
    else:
        print(r'Account/App '+str(appnum)+' The Microsoft key was uploaded successfully')
    return putstatus
    
#transfer 
for a in range(1, int(app_num)+1):
    client_id=os.getenv('CLIENT_ID_'+str(a))
    client_secret=os.getenv('CLIENT_SECRET_'+str(a))
    ms_token=os.getenv('MS_TOKEN_'+str(a))
    if a == 1:
        puturl=r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/MS_TOKEN'
    else:
        puturl=r'https://api.github.com/repos/'+gh_repo+r'/actions/secrets/MS_TOKEN_'+str(a)
    encrypted_value=createsecret(getpublickey(Auth,geturl),getmstoken(ms_token,a))
    setsecret(encrypted_value,key_id,puturl,a)
