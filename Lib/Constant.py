#! /usr/bin/python3
# coding=utf-8
"""
@Author  :   陈进文
@Contact :   jinwen.chen@luxshare-ict.com
@Software:   V2
@File    :   Constant.py
@Time    :   2022/8/17
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
@Desc    :   None
"""

RAW_TIMEOUT = 10
FAIL_STATUS_CODE = -1


class Status:
    SUCCESS = 0
    FAIL = 1


class ErrCode:
    EOF = -1
    TIMEOUT = -2
    FORMAT = -3
    KEY_NOT_EXIST = -4
    OVERRIDE = -5
    FileNotFound = -6
    INIT_PARAMS = -7
    PERMISSION_ERROR = -8
    SSH_SESSION = -9
    BMC_SESSION = -10
    SSH_CONNECTION = -11
    AUTHENTICATION = -12
    ELEMENT_NOT_FOUND = -13
    VALUE_ERROR = -14
    WEB_NAME_ERROR = -15
    URL_ADDR_ERROR = -16
    ITEM = -17
    SUITE = -18
    CMD = -19
    POWER_CHECK = -20
    RE_MATCH_FAIL = -21
    MY_ASSERT_ERROR = -22
    PDU_CONF_ERROR = -23


class Web:
    debug = True
    # timeout = 15
    timeout = 3
    implicitly_wait = 5
    # implicitly_wait = 45
    retry_count = 3
