from flask import Flask, redirect, request, jsonify, session, render_template

import requests
import urllib.parse
import datetime
import asyncio

from download_mp3 import download_song

app = Flask(__name__)

app.secret_key = 'kladsgjkl-ksdjngj-2895hngf'

CLIENT_ID = '3505e27080984a9d940b2125522e67f1'
CLIENT_SECRET = '6317ce38292f4d5e9bcba830f1b1e2d3'
REDIRECT_URI = 'http://localhost:8000/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token/'
API_BASE_URL = 'https://api.spotify.com/v1'

# homepage
@app.route('/')
def index():
    return '''
        Welcome to the app <a href=\"/login\">Login with Spotify</a>
        <br>
        <br>
        <a href=\"/logout\"> Log out </a>
    '''

# spotify login url
@app.route('/login')
def login():
    scope = 'user-read-private user-read-email user-library-read'
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialgo': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    return redirect(auth_url)

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

# callback route for when the user logs in successfully (or doesn't)
@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(url=TOKEN_URL, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.datetime.now().timestamp() + token_info['expires_in']

        return redirect('/songs')


# gettiing the user's saved songs
@app.route('/songs')
def tracks():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}",
    }

    results = []
    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        params = {
        'limit': 50,
        'offset': offset,
        'market': 'US'
        }
        response = requests.get(url=API_BASE_URL + '/me/tracks', headers=headers, params=params)
        curGroup = response.json()
        curGroup = curGroup['items']
        print(len(curGroup))

        for index, item in enumerate(curGroup):
            track = item['track']
            val = track['name'] + " - " + track['artists'][0]['name']
            results += [val]
        
        if len(curGroup) < 50:
            break
    
    data = {"songs": results}
    return render_template('index.html', data=data)


@app.route('/download/<string:song>')
async def download(song):
    await download_song(song)
    return "Your file has been downloaded"


# refreshing the access token token
@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(url=TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('/songs')


if __name__ == '__main__':
    app.run(port='8000', debug=True)

