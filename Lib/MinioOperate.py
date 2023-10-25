'''
@Author  :   Ben
@Contact :   Ben-ZC.Xie@luxshare-ict.com
@Software:   Cedar
@File    :   MinioOperate.py
@Time    :   2022/7/1
@Version :   1.0
@License :   Copyright ©LuxShare  2022 . All Rights Reserved.
@Desc    :   minio 上传下载数据
'''

from posixpath import split
from minio import Minio
from minio.error import ResponseError
import os, sys


class MinioOperate(object):
    def __init__(self):
        endpoint = os.environ['MINIO_SERVER']
        access_key = os.environ['MINIO_ACCESSKEY']
        secret_key = os.environ['MINIO_SECRETKEY']
        # bucket_name = os.environ['BUCKET_NAME']
        self.minioCient = Minio(endpoint,
                                access_key=access_key,
                                secret_key=secret_key,
                                secure=False)

    """
    注：创建桶命名限制：小写字母，句点，连字符和数字是
    唯一允许使用的字符（使用大写字母、下划线等命名会报错），长度至少应为3个字符
    """

    def createBucket(self, bucket_name):
        try:
            if self.minioCient.bucket_exists(bucket_name):  # bucket_exists：检查桶是否存在
                print("该存储桶已经存在")
            else:
                self.minioCient.make_bucket("pictures")
                print("存储桶创建成功")
        except ResponseError as err:
            print(err)
            sys.exit(-1)

    def uploadData(self, bucket_name, object_name, file_path, file_size=2):
        try:
            # 如果文件大于2M, 打包压缩上传
            fileSize = os.stat(file_path).st_size
            end = file_path.rindex('/')
            file = object_name.split('.')[0]
            gz_file_path = file_path[:end]
            if os.path.exists(os.path.join(gz_file_path, file)) and len(os.listdir(gz_file_path)) != 0:
                os.system('cd %s && tar -zcvf %s.tar.gz  %s %s' % (gz_file_path, file, object_name, file))
                object_name = file + '.tar.gz'
                file_path = gz_file_path + '/' + object_name
            else:
                if fileSize > file_size * 1024 * 1024:
                    os.system('cd %s && tar -zcvf %s.tar.gz  %s' % (gz_file_path, file, object_name))
                    object_name = file + '.tar.gz'
                    file_path = gz_file_path + '/' + object_name

            self.minioCient.fput_object(bucket_name, object_name, file_path)

            # if fileSize > file_size * 1024 * 1024:
            #     end = file_path.rindex('/')
            #     file = object_name.split('.')[0]
            #     gz_file_path = file_path[:end]
            #     if os.path.exists(os.path.join(gz_file_path, file)) and len(os.listdir(gz_file_path)) != 0:
            #         os.system('cd %s && tar -zcvf %s.tar.gz  %s %s'  % (gz_file_path, file, object_name, file))
            #     else:
            #         os.system('cd %s && tar -zcvf %s.tar.gz  %s'  % (gz_file_path, file, object_name))
            #     object_name = file + '.tar.gz'
            #     file_path = gz_file_path + '/' + object_name

            # self.minioCient.fput_object(bucket_name, object_name, file_path)
            print("%s upload Sussess" % object_name)
        except ResponseError as err:
            print(err)
            sys.exit(-1)

    def downloadData(self, bucket_name, object_name, file_path):
        try:
            self.minioCient.fget_object(bucket_name, object_name, file_path)
            print("Sussess")
        except ResponseError as err:
            print(err)
            sys.exit(-1)

# if __name__ == '__main__':
#     # bucket_name, object_name, file_path = 'test', 'black_whilte.json', '/root/scripts/ben/Cedar/Lib/black_whilte.json'
#     # MinioOperate().upload_object(bucket_name, object_name, file_path)

# bucket_name, object_name, file_path = 'test', 'UsbIdentifyRW-2022_07_21_16_06_50.log', '/root/scripts/ben/Cedar/Log/UsbIdentifyRW-2022_07_21_16_06_50.log'
# MinioOperate().uploadData(bucket_name, object_name, file_path)

#     bucket_name, object_name, file_path = 'test', 'UsbIdentifyRW-2022_07_21_16_06_50.log', '/root/scripts/ben/Cedar/UsbIdentifyRW-2022_07_21_16_06_50.log'
#     MinioOperate().downloadData(bucket_name, object_name, file_path)
