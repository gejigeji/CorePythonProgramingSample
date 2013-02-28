import requests
import json
import re
import random
from encrypt import encryptString
import os
import urllib2


class RenRen:

    def __init__(self, email=None, pwd=None):
	self.session =requests.Session()
	self.token = {}

    def login(self, email, pwd):
	key = self.getEncryptKey()

	if self.getShowCaptcha(email) == 1:
	    fn = 'icode.%s.jpg' % os.getpid()
            self.getICode(fn)
            print "Please input the code in file '%s':" % fn
            icode = raw_input().strip()
            os.remove(fn)
	else:
	    icode = ''
	
	data = {
	    'email': email,
	    'origURL': 'http://www.renren.com/home',
	    'icode': icode,
	    'domain': 'renren.com',
	    'key_id': 1,
	    'captcha_type': 'web_login',
	    'password':encryptString(key['e'], key['n'], pwd) if key['isEncrypt'] else pwd,
	    'rkey': key['rkey']
	    }
	print "login data: %s" % data
        url = 'http://www.renren.com/ajaxLogin/login?1=1&uniqueTimestamp=%f' % random.random()
        r = self.post(url, data)
        result = r.json()
        if result['code']:
            print 'login successfully'
            self.email = email
            r = self.get(result['homeUrl'])
            self.getToken(r.text)
        else:
            print 'login error', r.text
	

    def getICode(self, fn):
        r = self.get("http://icode.renren.com/getcode.do?t=web_login&rnd=%s" % random.random())
        if r.status_code == 200 and r.raw.headers['content-type'] == 'image/jpeg':
            with open(fn, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)
        else:
            print "get icode failure"
    

    def getShowCaptcha(self, email=None):
        r = self.post('http://www.renren.com/ajax/ShowCaptcha', data={'email': email})
        return r.json()
    

    def getEncryptKey(self):
	r = requests.get('http://login.renren.com/ajax/getEncryptKey')
	return r.json()

    def getToken(self, html=''):
        p = re.compile("get_check:'(.*)',get_check_x:'(.*)',env")

        if not html:
            r = self.get('http://www.renren.com')
            html = r.text

        result = p.search(html)
        self.token = {
            'requestToken': result.group(1),
            '_rtk': result.group(2)
        }

    def request(self, url, method, data={}):
	if data:
	    data.update(self.token)

	if method == 'get':
	    return self.session.get(url, data=data)
	elif method == 'post':
	    return self.session.post(url, data=data)

    def get(self, url, data={}):
	return self.request(url, 'get', data)

    def post(self, url, data={}):
	return self.request(url, 'post', data)

    def getUserInfo(self):
        r = self.get('http://notify.renren.com/wpi/getonlinecount.do')
        return r.json()

    def getNotifications(self):
        url = 'http://notify.renren.com/rmessage/get?getbybigtype=1&bigtype=1&limit=50&begin=0&view=17'
        r = self.get(url)
        try:
            result = json.loads(r.text, strict=False)
        except Exception, e:
            print 'error', e
            result = []
        return result

    def removeNotification(self, notify_id):
        self.get('http://notify.renren.com/rmessage/remove?nl=' + str(notify_id))

    def getDoings(self, uid, page=0):
        url = 'http://status.renren.com/GetSomeomeDoingList.do?userId=%s&curpage=%d' % (str(uid), page)
        r = self.get(url)
        return r.json().get('doingArray', [])

    def getDoingById(self, owner_id, doing_id):
        doings = self.getDoings(owner_id)
        doing = filter(lambda doing: doing['id'] == doing_id, doings)
        return doing[0] if doing else None

    def getDoingComments(self, owner_id, doing_id):
        url = 'http://status.renren.com/feedcommentretrieve.do'
        r = self.post(url, {
            'doingId': doing_id,
            'source': doing_id,
            'owner': owner_id,
            't': 3
        })

        return r.json()['replyList']

    def getCommentById(self, owner_id, doing_id, comment_id):
        comments = self.getDoingComments(owner_id, doing_id)
        comment = filter(lambda comment: comment['id'] == int(comment_id), comments)
        return comment[0] if comment else None

    def addComment(self, data):
        return {
            'status': self.addStatusComment,
            'album' : self.addAlbumComment,
            'photo' : self.addPhotoComment,
            'blog'  : self.addBlogComment,
            'share' : self.addStatusComment,
            'gossip': self.addGossip
        }[data['type']](data)

    def sendComment(self, url, payloads):
        r = self.post(url, payloads)
        r.raise_for_status()
        return r.json()


    # visit sb.
    def visit(self, uid):
        self.get('http://www.renren.com/' + str(uid) + '/profile')
    
    

if __name__ == '__main__':
    renren = RenRen()
    renren.login('654428746@qq.com', 'lina368520')
    info = renren.getUserInfo()
    noti = renren.getNotifications()
    print 'hello', info['hostname']

    owner_id = '422703493'#gejigeji
    #owner_id = '301426360'#piaobidao
    #owner_id = '308574541'#lina
    doings = renren.getDoings(owner_id)

    for i in range(len(doings)):
	print '---'*24,'\r\n','---'*24
	print doings[i]['id'], doings[i]['content'],'---',doings[i]['dtime']
	doing_id = str(doings[i]['id'])[:-2]
	doingcomments = renren.getDoingComments(owner_id,doing_id)
	#print doingcomments
	
	for j in range(len(doingcomments)):
	    print '---'*12
	    print doingcomments[j]['replyContent'],'---',doingcomments[j]['replyTime']
