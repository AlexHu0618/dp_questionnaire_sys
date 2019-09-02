#! /usr/bin/env python3
# encoding:utf-8

# -*- coding: utf-8 -*-
# @Time    : 8/22/19 5:48 PM
# @Author  : Alex Hu
# @Contact : jthu4alex@163.com
# @FileName: app.py
# @Software: PyCharm
# @Blog    : http://www.gzrobot.net/aboutme
# @version : 0.0.0

import os
from app import create_app
from flask_script import Manager
from myLogger import mylogger


app = create_app(os.getenv('FLASK_CONFIG') or 'default')  # can set environment variable 'FLASK_CONFIG', \
                                                            # or use the config.py
manager = Manager(app)


# def make_shell_context():  # register the callback function for shell to avoid loading list every shell start
#     return dict(app=app, db=db)
#
#
# manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == '__main__':
    mylogger.info("Run program, start!")
    manager.run()
