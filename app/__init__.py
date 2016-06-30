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

import os
import logging
from flask import Flask
from flask_bootstrap import Bootstrap
from flask.ext.pymongo import PyMongo
from logging.handlers import RotatingFileHandler
# from mongokit import Connection


def create_app(config='config.py', islogging=True):
    app = Flask(__name__)
    app.config.from_object('app.config')
    Bootstrap(app)
    app.mongo = PyMongo(app)
    if islogging:
        log_file = os.path.join(app.config['LOG_DIR'], 'log.log')
        file_handler = RotatingFileHandler(log_file, 'a',
                                           1 * 1024 * 1024, 10)
        formatter = logging.Formatter(
            '%(asctime)s : %(message)s [in %(pathname)s:%(lineno)d]')
        file_handler.setFormatter(formatter)
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('Run Tankstelle App')

    return app

app = create_app()

from app import views
