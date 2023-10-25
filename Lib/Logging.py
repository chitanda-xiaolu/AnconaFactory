#! /usr/bin/python3
# coding=utf-8
"""
@Author  :   陈进文
@Contact :   jinwen.chen@luxshare-ict.com
@Software:   V2
@File    :   Logging.py
@Time    :   2022/8/17
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
@Desc    :   None
"""

import logging
import time
import os

from .Error import FormatError


def get_file_name(file_path):
    """[summary]

    Args:
        file_path ([str]): [file name abcpath]

    Raises:
        TypeError: [not string]
        FormatError: [endswith not .py]

    Returns:
        [str]: [generate a name]
    """
    # check file name is str
    if not isinstance(file_path, str):
        raise TypeError("file name is string")
    # check file name format
    if not file_path.endswith(".py"):
        raise FormatError("file name must be .py")
    file_name = os.path.basename(file_path)
    new_name = file_name.replace(".py", "")
    return new_name


class LogPath(object):
    def __init__(self, case_name, folder=None, sub_folder=None):
        # def __init__(self, case_name, folder=None):
        if folder is None or folder == '':
            if sub_folder:
                self.__dir = os.path.join(self.find_root(__file__), "Log", sub_folder)
            else:
                self.__dir = os.path.join(self.find_root(__file__), "Log")
            # self.__dir = os.path.join(self.find_root(__file__), "Log")
        else:
            self.__dir = folder
        self.case_name = case_name

    def find_root(self, abspath_):
        file_name = os.path.basename(abspath_)
        folder = os.path.dirname(abspath_)
        if file_name == "Lib":
            return folder
        else:
            return self.find_root(folder)

    @property
    def logfile(self):
        return self.__dir

    def get_log_folder(self):
        return self.__dir

    def path_gen(self):
        log_dir = self.__dir
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        return log_dir

    def log_name(self):
        log_dir = self.path_gen()
        time_tag = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        # case_name = get_file_name(sys.argv[0])

        # log_name = os.path.join(log_dir, "%s.log" % (str(case_name) + '-' + time_tag))
        log_name = os.path.join(log_dir, "%s.log" % (str(self.case_name) + '-' + time_tag))
        return log_name


class LoggerGet(object):
    def __init__(self, case_name, log_flag, folder=None, sub_folder=None):
        # def __init__(self, case_name, log_flag, folder=None):
        log = LogPath(case_name, folder, sub_folder)
        # log = LogPath(case_name, folder)
        self.path = log.path_gen()
        log_name = log.log_name()
        self.html_name = log_name.replace(".log", ".html")
        self.logger = logging.getLogger(self.path)
        self.logger.setLevel(logging.DEBUG)
        if sub_folder:
            put = sub_folder.split("_")[0]
            self.fmt = logging.Formatter(f'[{put}]---[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        else:
            self.fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
        if not self.logger.handlers:
            self.sh = logging.StreamHandler()  # for print out
            self.sh.setFormatter(self.fmt)
            self.logger.addHandler(self.sh)
        self.fh = logging.FileHandler(log_name, encoding="UTF-8")  # for file out
        self.fh.setFormatter(self.fmt)
        self.logger.addHandler(self.fh)
        if log_flag == "normal":
            self.sh.setLevel(30)  # change print out level
            self.fh.setLevel(10)  # change file out level:debug:10
        elif log_flag == "debug":
            self.sh.setLevel(10)  # change print out level
            self.fh.setLevel(10)  # change file out level:debug:10

        setattr(self.logger, "sh", self.sh)
        setattr(self.logger, 'log_name', log_name)

    def debug(self, msg, *args, **kwargs):
        self.logger.name = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.name = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.name = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.name = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self.logger.name = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
        self.logger.critical(msg, *args, **kwargs)

    def get_name(self):
        return self.logger.log_name
