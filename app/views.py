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


from app import app
from app import util
# from requests import get
from flask import jsonify
from flask import request
from flask import render_template


def error(msg):
    return jsonify({'error': msg, 'status': 'error'})


@app.route('/test')
def hello_world():
    return 'Hello world!'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        query = request.form['query']
        if not query:
            return error("Inserted query is empty")

    try:
        cord = util.coordination(query)
    except util.AddressError as e:
        return error(str(e))

    lat, lng = cord
    formated = util.get_formatted_data(lat, lng)
    return jsonify(formated)


@app.route('/find')
def find_stations():
    try:
        lat, lng = request.args['cord'].split(',')
    except:
        return
    formated = util.get_formatted_data(lat, lng)
    return jsonify(formated)


# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('404.html'), 404


# @app.errorhandler(500)
# def internal_error(error):
#     return render_template('500.html'), 500
