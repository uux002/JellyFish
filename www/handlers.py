#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio

import markdown2


from aiohttp import web

from coroweb import get, post
from apis import Page, APIValueError, APIResourceNotFoundError, APIError

from models import Account, User,TruthOrDare,Comment, next_id
from config import configs

from http import cookies

COOKIE_NAME = 'zhenxinhuadamaoxian_01'
_COOKIE_KEY = configs.session.secret

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

def set_cookie(name,value):
    # ==============> TODO: Set Cookie
    '''
    c = cookies.SimpleCookie()
    c.httponly = True
    c.max_age = 86400
    c[name] = value
    print("Content-type: text/plain")
    print(c.output())
    print('')
    print('Cookie set with: ' + c.output())
    '''

def validate_email(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return True
    return False

def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()

def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

def account2cookie(account, max_age):
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (account.id,account.passwd, expires, _COOKIE_KEY)
    L = [account.id,expires,hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

def cookie2account(cookie_str):
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid,expires,sha1 = L
        if int(expires) < time.time():
            return None
        account = yield from account.find(uid)
        if account is None:
            return None
        s = '%s-%s-%s-%s' % (uid, account.passwd, expires,_COOKIE_KEY)
        if sh1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            return None
        account.passwd = '******'
        user = User.find('account_id=?',[uid])
        if user is None:
            return None
        return user
    except Exception as e:
        logging.exception(e)
        return None


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)

@get('/')
def index(request):
    if request.__user__ is not None:
        logging.info("######### Request" + request.__user__.nickname)
    else:
         logging.info("--------------$$$ No User") 

    return {
        '__template__': 'index.html',
        '__user__': request.__user__,
    }

@get('/signinsignup')
def signin_or_signup():
    return {
        '__template__':'signinsignup.html',
    }

@get('/signin')
def signin():
    return{
        '__template__': 'signin.html',
    }

@get('/signout')
def signout():
    pass

@get('/signup')
def signup():
    return{
        '__template__': 'signup.html'
    }

@get('/user/{id}')
def get_user_profile(id):
    pass

@get('/public')
def public_item():
    return{
        '__template__': 'public.html'
    }

@get('/zhenxinhua')
def get_zhenxinhua():
    pass

@get('/damaoxian')
def get_damaoxian():
    pass

@get('/zhenxinhua/{id}')
def get_zhenxinhua_by_id(id):
    return{
        '__template__': 'zhenxinhua.html'
    }

@get('/damaoxian/{id}')
def get_damaoxian_by_id(id):
    return{
        '__template__': 'damaoxian.html'
    }


# -------------------- APIs --------------------
@post('/api/signin')
async def api_authenticate(*,email,password):
    if not email:
        return {
            'result':-1,
            'msg':'邮箱地址不合法'
        }

    if not password:
        return {
            'result':-1,
            'msg':'密码错误'
        }

    accounts = await Account.findAll('email=?',[email])
    if len(accounts) == 0:
        return {
            'result':-1,
            'msg':'邮箱地址不存在'
        }

    account = accounts[0]
    sha1 = hashlib.sha1()
    sha1.update(account.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(password.encode('utf-8'))

    if account.passwd != sha1.hexdigest():
        return {
            'result':-1,
            'msg':'密码错误'
        }
        
    set_cookie(COOKIE_NAME,account2cookie(account,86400))
    #r = web.Response()
    #r.set_cookie(COOKIE_NAME, account2cookie(account,86400),max_age=86400,httponly=True)
    account.passwd = '******'

    return {
        'result':0,
        'msg':'登录成功'
    }

@get('/api/user')
def api_get_user(*,id):
    pass

@get('/api/zhenxinhuadamaoxian')
def api_get_zhenxinhuadamaoxian(*, page='1'):
    pass

@get('/api/zhenxinhua')
def api_get_zhenxinhua(*, page='1'):
    pass

@get('/api/damaoxian')
def api_get_damaoxian(*, page='1'):
    pass

@post('/api/users')
async def api_register_user(*, nickname, email, password):
    if not nickname or not nickname.strip():
        return {
            'result':-1,
            'msg':"昵称最好不要为空噢"
        }
    
    if not email or not validate_email(email):
        return {
            'result':-1,
            'msg':'你的邮箱好像是假的哎'
        } 

    if not password or not password.strip():
        return {
            'result':-1,
            'msg':'你的密码是假的吧，能不能想个好一点的'
        }
    
    accounts = await Account.findAll('email=?',[email])
    if len(accounts) > 0:
        return {
            'result':-1,
            'msg':'你的邮箱已经被注册了'
        }
        
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid,password)
    hexdigest = hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest()
    account = Account(id=uid, email=email, passwd=hexdigest)
    logging.info(">>>>>>>>>>>>>>> uid:" + account.id)
    logging.info(">>>>>>>>>>>>>>> email:" + account.email)
    logging.info(">>>>>>>>>>>>>>> password:" + account.passwd)
    await account.save()

    user = User(id=next_id(),account_id=uid,nickname=nickname)
    await user.save()

    #r = web.Response()
    #r.set_cookie(COOKIE_NAME, account2cookie(account, 86400), max_age=86400, httponly=True)

    set_cookie(COOKIE_NAME,account2cookie(account,86400))

    logging.info("==============> On Register Function") 
    logging.info("===========> %s %s %s" % (nickname, email, password))

    return {
        'result':0,
        'msg':'注册成功'
    }


@post('/api/public')
def api_public():
    pass

@post('/api/public_comment')
def api_public_comment():
    pass

@get('/api/comments')
def api_get_comments(*, page='1'):
    pass



# ------------------------------------------------------------------ Ready Deleted Code ------------------------------------------------------------------

'''
@get('/')
def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }
    '''

@get('/blog/{id}')
def get_blog(id):
    blog = yield from Blog.find(id)
    comments = yield from Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }


@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }

@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }

@post('/api/authenticate')
def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    users = yield from User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r

@get('/manage/blogs/create')
def manage_create_blog():
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'
    }

'''

@post('/api/users')
def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = yield from User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    yield from user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r
'''

@get('/api/blogs')
def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = yield from Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = yield from Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)

@get('/api/blogs/{id}')
def api_get_blog(*, id):
    blog = yield from Blog.find(id)
    return blog


@post('/api/blogs')
def api_create_blog(request, *, name, summary, content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, name=name.strip(), summary=summary.strip(), content=content.strip())
    yield from blog.save()
    return blog