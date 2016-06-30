# Copyright (c) 2015, 2016,  Mohammed Hassan Zahraee

# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are not permitted.

# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form is only allowed with copyright holder
# permission

# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

'''
Author: Mohammad Hassan Zahraee.
'''

import os
import time
import flask.ext.pymongo as pymongo
from app import app
from requests import get


class AddressError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


def coordination(search_query):
    '''Returns coordination for a postal code or an address after querying from
    Google Maps
    Raise Exception if:
        Address is outside Germany
        couldn't be found
        or couldn't get a valid response from Google Maps API
    '''
    try:
        int(search_query)
        query = 'DE-' + str(search_query)
    except:
        query = search_query

    collection = app.mongo.db.locations
    cord = _get_cache(collection, query, 60 * 60 * 24 * 10)     # 10 days
    if cord:
        return cord
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': query,
              'key': app.config['GOOGLEMAP_KEY']}
    resp = get(base_url, params)
    rjson = resp.json()

    if rjson['status'] == 'OK':
        formatted_add = rjson['results'][0]['formatted_address']
        if 'Germany' in formatted_add:
            cord = (str(rjson['results'][0]['geometry']['location']['lat']),
                    str(rjson['results'][0]['geometry']['location']['lng']))
        else:
            raise AddressError('Address is not inside Germany')
    else:
        raise AddressError("Couldn't find the address")
    _set_cache(collection, query, cord)
    return cord


def format_data(station):
    s = station
    brand = s['brand']
    if brand is None or brand == "":
        brand = s['name']
    return {'name': (brand + ' ' + s['street'])[:30],
            'long_name': s['name'],
            'dist': s['dist'],
            'lat': s['lat'],
            'lng': s['lng'],
            'address': u'{} {}, {} {}'.format(s.get('street', ''),
                                              s.get('houseNumber', ''),
                                              s.get('postCode', ''),
                                              s.get('place', '')
                                              ),
            'data': [s.get('e5', 0),
                     s.get('e10', 0),
                     s.get('diesel', 0)
                     ]
            }


def get_key(station):
    """Returns sorting key for station sorting based on price"""
    try:
        key = float(station[get_key.sort_by])
        if key == 0 or not key:
            key = 9999  # A big enough number
    except:
        key = 9999
    return key


def list_prices(lat, long, radius, sort_by='e5'):
    '''Returns list of gas stations for a coordination
    The result is basically tankerkoenig response with closed gas stations
    filtered and then stations sorted by price of "sort_by" and the closest
    station based on "dist" field in response.
    '''

    collection = app.mongo.db.prices
    data_id = "{}:{}:{}".format(lat, long, radius)

    json = _get_cache(collection, data_id)
    if not json:
        args = {'lat': lat,
                'lng': long,
                'rad': radius,
                'sort': 'dist',     # when type is 'all' sort must be dist
                'type': 'all',
                'apikey': app.config['API_KEY']}
        url = 'https://creativecommons.tankerkoenig.de/json/list.php'
        json = get(url, params=args).json()
        _set_cache(collection, data_id, json)

    if not json["ok"]:
        print json
        app.logger.info('error in listing' + str(json))
        result = json
    else:
        stations = filter(lambda station: station['isOpen'], json["stations"])

        if stations:
            stations = sorted(stations, key=lambda station: station['dist'])
            closest = stations[0]
            get_key.sort_by = sort_by       # Awesome Trick
            stations = sorted(stations, key=get_key)[:7]    # Top 7 result
            result = {'stations': stations,
                      'closest': closest}
        else:
            result = None

    return result


def get_formatted_data(lat, lng):
    radius = 3
    while radius < 20:
        res = list_prices(lat, lng, radius)
        if res:
            break
        radius = int(radius * 1.5)

    formated = [format_data(station) for station in res['stations']]
    closest = format_data(res['closest'])

    place = res['stations'][0]['place']
    hourly_e5 = hourly_avg(place)
    hourly_diesel = hourly_avg(place, 'diesel')
    hourly = [hourly_e5, hourly_diesel]

    formated = {'stations': formated,
                'closest': closest,
                'hourly': hourly,
                'status': 'OK'}
    return formated


def _get_cache(collection, data_id, valid_age=300):
    return
    """
    :arg int valid_age default to 5 minutes
    """
    cache = collection.find({'data_id': data_id})
    cache = cache.sort('timestamp', pymongo.DESCENDING)[0]
    cache_age = 0
    data = None

    if cache:
        cache_age = time.time() - cache.get('timestamp',
                                            time.mktime(time.gmtime(0)))
        if cache_age < valid_age:
            data = cache['data']

    return data


def _set_cache(collection, data_id, data):
    """Set cache data

    :arg str collection: Mongo collection to save into cache. (required)
    :arg str data_id: Cache ID of data. (required)
    :arg str data: Data to save into cache. (required)
    """
    document = {
        'data_id': data_id,
        'timestamp': time.time(),
        'hour': hour(),
        'data': data,
    }
    collection.insert_one(document)


def hour():
    """Returns current hour in Berlin
        if it's past half hour will be rounded to next hour
        0 < return value < 23
    """
    os.environ['TZ'] = 'Europe/Berlin'
    time.tzset()
    hour = int(time.strftime('%H'))
    round_val = 0
    if int(time.strftime('%M')) > 30:
        round_val = 1     # 09:40 -> 10
    return hour + round_val


def hourly_avg(place, fuel_type='e5'):
    # collection = app.mongo.db.prices
    # intentionaly removed code
    pass
