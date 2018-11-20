# -*- coding: UTF-8 -*-
#! python36
#在Python2中是首字母大写的
import socketserver
import time,sys,datetime
import socket, struct, os
from sklearn import svm
from sklearn.externals import joblib
import csv
from source.csvDataPrc import csvDataPrc as csvDP
from source.gentic_algorithm import GA as ga
# from source.gentic_algorithm import *
#服务器ip地址
HOST = '219.216.65.188'
#服务器端口
PORT = 4554


class TCPhandler(socketserver.BaseRequestHandler):
    # LastPid = 'lasePid'
    # flag=True
    Pre_currentRecord=0
    Train_currentRecord= 0
    res = 'legal\n'

    def handle(self):
        print("\033[0;31m%s\033[0m" % "Connected by", self.client_address)

        print(datetime.datetime.now().strftime('%Y %m %d %H:%M:%S:%f'))
        #print('connected from:', self.client_address)
        print('test用户连接成功！')

        # # 定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
        # fileinfo_size = struct.calcsize('128sl')
        # self.buf = self.request.recv(fileinfo_size)
        # print(self.buf)
        # if self.buf:  # 如果不加这个if，第一个文件传输完成后会自动走到下一句
        #     self.filename, self.filesize = struct.unpack('128sl', self.buf)
        #     # 根据128sl解包文件信息，与client端的打包规则相同
        #     print('filesize is: ', self.filesize, 'filename size is: ', len(self.filename), 'filename is:', self.filename)
        #     # 文件名长度为128，大于文件名实际长度
        #     # os.getcwd()获取当前目录，获取的是本文件所在的文件夹的路径。
        #     newFilename = 'new_'+(self.filename).decode('utf-8')
        #     print(newFilename)
        #     currentPath = str(os.getcwd())
        #     self.filenewname = os.path.join(currentPath,newFilename).strip('\00')
        #
        #     # 使用strip()删除打包时附加的多余空字符
        #     print('OKOK',self.filenewname, type(self.filenewname))
        #     recvd_size = 0  # 定义接收了的文件大小
        #     file = open(self.filenewname, 'wb+')
        #     print('stat receiving...')
        #     while not recvd_size == self.filesize:
        #         if self.filesize - recvd_size > 1024:
        #             rdata = self.request.recv(1024)
        #             recvd_size += len(rdata)
        #         else:
        #             rdata = self.request.recv(self.filesize - recvd_size)
        #             recvd_size = self.filesize
        #         file.write(rdata)
        #     file.close()
        #     print('receive done')
        #     msg = 'recv is OK,the server send msg to client!'
        #     self.request.send(msg.encode(encoding='utf-8'))
        # else:
        # print("nonono")
        # # infinite loop

        #接收消息
        while True:
            # get user_id and file_length
            # len,userid,Touch,2018-06-04 09:31:23,0,SYN_REPORT,cn.nubia.launcher
            self.header = self.request.recv(1024)
            # print("self.header:")
            # print(self.header)
            self.header = self.header.decode()
            self.header = self.header.split('\r\n')
            # print(self.header)
            if self.header[0]:
                recordlen = int(self.header[0])
            else:
                recordlen = 0
                continue
            print("self.header[0]:")
            # print(recordlen)
            userid = self.header[1]
            # print("self.header[1]:")
            # print(userid)

            # ACK
            self.request.send("header ok \r\n".encode())
            # print("\033[0;31m%s\033[0m" % "Header  ok! len:", recordlen,"   userid:",userid)

            recordCon = bytes()
            while recordlen > 0:
                data = self.request.recv(recordlen)
                recordlen -= len(data)
                recordCon = recordCon + data
                # self.header[2]+','+self.header[3]+','+self.header[4]+','+self.header[5]+','+self.header[6]
            recordCon = recordCon.decode()
            recordConList = recordCon.split('\n')
            recordCon = recordConList[0]
            print("接收到的内容为：")
            print(recordCon)
            print(datetime.datetime.now().strftime('%H:%M:%S.%f'), "record recv finished")

            #获取当前记录的PId
            recordList = recordCon.split(',')#将pid后边的空格去掉
            print(recordList)
            Pid = recordList[4]
            # 提取出pid
            # Pid = Pid.replace("\r\n","")
            print('Pid is :',Pid)
            # record = recordCon+'\r\n'
            # # 第一次获取到LastPid,只做一次
            # if (self.flag):
            #     self.flag = False
            #     self.LastPid= Pid
            # 记录上一条pid
            recordCon = recordCon+"\n"

            # 判断相关目录是否存在
            if not os.path.exists('../'+userid+'_best_modles/'):
                os.makedirs('../'+userid+'_best_modles/')
            if not os.path.exists('../'+userid+'_predict_files/'):
                os.makedirs('../'+userid+'_predict_files/')
            if not os.path.exists('../'+userid+'_train_files/'):
                os.makedirs('../'+userid+'_train_files/')
            if not os.path.exists('../'+userid+'_Valiable_dataFiles/'):
                os.makedirs('../'+userid+'_Valiable_dataFiles/')

            # 判断是否有Pid对应的模型
            module_file = '../'+userid+'_best_modles/'+Pid+'_model.m'
            predictFlieName = '../' + userid + '_predict_files/' + Pid + '.csv'
            trainFileName = '../' + userid + '_train_files/' + Pid + '.csv'

            print(module_file)

            if(os.path.exists(module_file)):
                #     模型存在，进行预测
                print("module 存在")

                # 获取当前文件的行数!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!一直是0

                # 首先判断是否存在文件
                #     why 不使用open（，"w"）呢，这个可以不存在自动创建，但是如果存在读不了行数
                if(not os.path.isfile(predictFlieName)):
                    open(predictFlieName,"w").close()

                predict_file = open(predictFlieName)
                self.Pre_currentRecord = len(predict_file.readlines())
                predict_file.close()

                print("当前预测集记录数目：")
                print(self.Pre_currentRecord)
                #   判断是否满足预测的文件的要求（达到8条数据）
                if(self.Pre_currentRecord>=20):
                    print("进行预测")
                    # 将预测集文件传入
                    # 对预测集文件进行处理,得到数据集
                    myTestCsvDP = csvDP(predictFlieName)
                    myTestCsvDP = myTestCsvDP.set()

                    # 调用模型进行相应的预测
                    clf = joblib.load(module_file)
                    # 得到的预测结果是一个数组，但是我们期望的是仅仅含有一个元素的数组
                    # 所以，我们这样判断，假若数组中含有一个-1的话那么即为非法，也就是我们不容许有非法的
                    pre_result = clf.predict(myTestCsvDP)
                    print("当前预测集结果数组：")
                    print(pre_result)

                    # 非法用户(改成了一半以上的-1就认定为非法用户)
                    nums_error = pre_result[pre_result == -1].size
                    if nums_error >= 0.5*(pre_result.size):
                        self.res = 'illegal\n'

                    # 清空文件需要先打开文件
                    predict_file = open(predictFlieName, "w")
                    predict_file.seek(0)
                    predict_file.truncate()  # 清空预测集文件
                    predict_file.close()

                else:
                    # 预测集没有达到符合的大小
                    print("追加到预测集文件中")
                    predict_file = open(predictFlieName,"a+")
                    predict_file.write(recordCon)
                    predict_file.close()
            else:
                #模型不存在，进行训练
                print('模型不存在')
                # 从当前的训练集文件中加载record数目,
                # ！！！！！！！！！！！！！以"a+"的形式打开读到文件的行数为0
                # ！！！！！！！所以读取文件行数，先打开在关闭，再以a+的形式追加

                # 首先判断是否存在文件
                #     why 不使用open（，"w"）呢，这个可以不存在自动创建，但是如果存在读不了行数
                if (not os.path.isfile(trainFileName)):
                    open(trainFileName, "w").close()

                train_file = open(trainFileName)
                self.Train_currentRecord = len(train_file.readlines())
                train_file.close()
                # 判断训练集的个数，达到2000条开始训练
                print("当前训练集文件的记录数目:")
                print(self.Train_currentRecord)
                if(self.Train_currentRecord>2000):
                    #开始训练
                    print('开始训练time')
                    timeoutputfile = open('timeSave.txt','a')
                    startTime = datetime.datetime.now().strftime('%H:%M:%S.%f')
                    print(datetime.datetime.now().strftime('%H:%M:%S.%f'),timeoutputfile)
                    timeoutputfile.close()

                    print('保存模型')
                    # 对数据进行处理，得到真正的数据集CSVData
                    print('对record进行处理得到数据集data')
                    Val_data = csvDP(trainFileName)
                    # print(type(Val_data))
                    Valiable_Data = Val_data.set()
                    # print(type(Valiable_Data))
                    # 将数据集划分成TrainD和TestD ，留出法，随机的选择百分之30作为测试集
                    #需要改动，这个数据取的不好
                    print('将数据集用“留出法”来进行处理，划分成训练集和测试集')
                    total = len(Valiable_Data)
                    TrainD = Valiable_Data[0:int(0.3*total)]
                    TestD = Valiable_Data[int(0.3*total):]

                    # 调用GA_OCSVM
                    theGa = ga(TrainD, TestD, userid, Pid)
                    # 训练并保存模型,对于GA的一个参数的初始状态，是自己设置的，可以再调节
                    theGa.funGA(100,0.5,0.6,100)
                    print("训练以及保存模型time")
                    timeoutputfile = open('timeSave.txt', 'a')
                    print(datetime.datetime.now().strftime('%H:%M:%S.%f'), timeoutputfile)
                    endTime = datetime.datetime.now().strftime('%H:%M:%S.%f')
                    timeSum = endTime-startTime
                    print("训练时间:")
                    print(timeSum)
                    timeoutputfile.close()

                else:
                    #追加到训练集中
                    train_file = open(trainFileName, 'a+')
                    train_file.write(recordCon)
                    print("追加到训练集数据")
                    train_file.close()

            print("响应消息为:", "\033[0;31m%s\033[0m" % self.res)
            #send the predict_results
            self.request.send((self.res).encode())
            print("响应消息发送成功!")

if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer((HOST, PORT), TCPhandler)
    server.serve_forever()