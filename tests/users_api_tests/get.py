from requests import get, post, put, delete
from pprint import pprint

API_URL = 'http://localhost:80/api/'

pprint(get(API_URL + 'users').json())
pprint(get(API_URL + 'users/1').json())

pprint(get(API_URL + 'users/100').json())
pprint(get(API_URL + 'users/abc').json())