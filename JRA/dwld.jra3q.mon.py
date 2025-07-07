#!/usr/bin/env python3

#download and covert to netcdf

yrstrt,yrlast,mnstrt,mnlast=2017,2024,1,12
field='fcst_phy3m'
freq='Monthly'

import urllib.request
import urllib.parse
import http.cookiejar
import html.parser
import subprocess
import sys
import os


import argparse
import base64
import netrc
import getpass


class CASLoginParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.action = None
        self.data = {}

    def handle_starttag(self, tagname, attribute):
        if tagname.lower() == 'form':
            attribute = dict(attribute)
            if 'action' in attribute:
                self.action = attribute['action']
        elif tagname.lower() == 'input':
            attribute = dict(attribute)
            if 'name' in attribute and 'value' in attribute:
                self.data[attribute['name']] = attribute['value']

class DIASAccess():
    def __init__(self, username, password):
        self.__cas_url = 'https://auth.diasjp.net/cas/login?'
        self.__username = username
        self.__password = password
        self.__cj = http.cookiejar.MozillaCookieJar()
        self.__opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.__cj))

    def open(self, url, data=None):
        if data is not None:
            data = data.encode('utf-8')
        response = self.__opener.open(url, data)
        response_url = response.geturl()

        if response_url != url and response_url.startswith(self.__cas_url):
            # redirected to CAS login page
            response = self.__login_cas(response)
            if data is not None:
                # If POST (data != None), need reopen
                response.close()
                response = self.__opener.open(url, data)

        return response

    def __login_cas(self, response):
        parser = CASLoginParser()
        parser.feed(response.read().decode('utf-8'))
        parser.close()

        if parser.action is None:
            raise LoginError('Not login page')

        action_url = urllib.parse.urljoin(response.geturl(), parser.action)
        data = parser.data
        data['username'] = self.__username
        data['password'] = self.__password

        response.close()
        response = self.__opener.open(action_url, urllib.parse.urlencode(data).encode('utf-8'))

        if response.geturl() == action_url:
            print('Authorization fail')
            quit()

        return response

    def dl(self, url, path, file, data=None):
        try:
            if data is not None:
                data = data.encode('utf-8')
            response = self.__opener.open(url, data)
            if not os.path.exists('.' + path):
                os.makedirs('.' + path)

            with open('.' + path + file, 'wb') as f:
                file_size_dl = 0
                block_size = 8192
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break

                    file_size_dl += len(buffer)
                    f.write(buffer)

            print(path + file + "  OK")
            return response

        except urllib.error.HTTPError as e:
            print(path + file + "  NG")


class LoginError(Exception):
    def __init__(self, e):
        super().__init__(e)

if __name__ == '__main__':
    host = 'data.diasjp.net'

    usage = '''usage: scriptdl.py [options]'''
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument('-n', '--netrc', default=None,
                        help='specify the netrc file', metavar='FILE')
    parser.add_argument('-u', '--user', default=None,
                        help='specify the DIAS account name',
                        metavar='USERNAME')

    args = parser.parse_args()

    login = None
    password = None

    try:
        if args.netrc:
            auth = netrc.netrc(args.netrc).authenticators(host)
            if auth is not None:
                login, account, password = auth
    except (IOError):
        pass

    if args.user is not None:
        login = args.user
        password = None

    if login is None:
        login = input('Username: ')

    if password is None:
        password = getpass.getpass('Password: ')

    access = DIASAccess(login, password)

    targeturl = 'https://data.diasjp.net/dl/storages/filelist/dataset:645'
    response = access.open(targeturl)
    response.close()
  
    DayofMonth={1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

    for iyr in range(yrstrt,yrlast+1,1):
        diri='/JRA3Q/Hist/Monthly/{:s}/'.format(field)
        '''
        # 2-D field like 'fcst_phy2m125'
        for fili in ['{:s}.{:s}.ctl'.format(field,freq.lower()),'{:s}.{:s}.idx'.format(field,freq.lower())]:
            if os.path.exists('.'+diri+fili):continue
            decoded_link=base64.b64encode('{:s}{:s}'.format(diri,fili).encode('utf-8')).decode('utf-8')
            access.dl('https://data.diasjp.net/dl/storages/downloadCmd/'+decoded_link, diri,fili)

        for imon in range(mnstrt,mnlast+1):
            fili='{:s}.{:04d}{:02d}'.format(field,iyr,imon)
            if os.path.exists('.'+diri+fili) or os.path.exists('.'+diri+fili+'.nc'):continue
            decoded_link=base64.b64encode('{:s}{:s}'.format(diri,fili).encode('utf-8')).decode('utf-8')
            access.dl('https://data.diasjp.net/dl/storages/downloadCmd/'+decoded_link, diri,fili)
            os.system('cdo -f nc copy {:s} {:s}'.format('.'+diri+fili,'.'+diri+fili+'.nc'))
            os.system('rm {:s}'.format('.'+diri+fili))
            
        '''

      
        # 3-D fields like "fcst_phy3m_adhr.194709"
        for ivar in ['adhr','cnvhr','lrghr','vdfhr']:          
            for fili in ['{:s}_{:s}.{:s}.ctl'.format(field,ivar,freq.lower()),'{:s}_{:s}.{:s}.idx'.format(field,ivar,freq.lower())]:
                if os.path.exists('.'+diri+fili):continue
                decoded_link=base64.b64encode('{:s}{:s}'.format(diri,fili).encode('utf-8')).decode('utf-8')
                access.dl('https://data.diasjp.net/dl/storages/downloadCmd/'+decoded_link, diri,fili)          
            for imon in range(mnstrt,mnlast+1):  
                fili='{:s}_{:s}.{:04d}{:02d}'.format(field,ivar,iyr,imon)
                if os.path.exists('.'+diri+fili) or os.path.exists('.'+diri+fili+'.nc'):continue
                decoded_link=base64.b64encode('{:s}{:s}'.format(diri,fili).encode('utf-8')).decode('utf-8')
                access.dl('https://data.diasjp.net/dl/storages/downloadCmd/'+decoded_link, diri,fili)
                
                os.system('cdo -f nc copy {:s} {:s}'.format('.'+diri+fili,'.'+diri+fili+'.nc'))
                os.system('rm {:s}'.format('.'+diri+fili))
          
