# -*- coding: UTF-8 -*-
#! python36
#在Python2中是首字母小写的
import socketserver
#from keras.models import load_model
import time
import socket, struct, os

#cls = classfiy_OCS('test')
#cls.test_model()

#服务器ip地址
HOST = '202.199.6.212'
#服务器端口
PORT = 2047

class TCPhandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("\033[0;31m%s\033[0m" % "Connected by", self.client_address)
        print('connected from:', self.client_address)

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
            self.header = self.request.recv(1024)
            print(self.header)
            self.header = self.header.decode()
            self.header = self.header.split('\r\n')
            filelen = int(self.header[0])
            userid = self.header[1]

            # ACK
            self.request.send("header ok\r\n".encode())
            print("\033[0;31m%s\033[0m" % "    Header ok", filelen,
                  "  userid", userid)

            # receive file data
            file = bytes()
            while filelen > 0:
                data = self.request.recv(8192)
                filelen -= len(data)
                file = file + data
            print("the file is :",file," !!!!")
            print(time.strftime('%Y-%m-%d %H:%M:%S'), "file recv finished")
            # save file
            tfile = open(userid + '.csv', 'a+')
            tfile.write(file.decode())
            tfile.close()

            # get predict res
            # res = cls.predict()
            res= 'illegal user'
            print("res:", "\033[0;31m%s\033[0m" % res)
            res = res + "\r\n"
            #send the predict_results
            self.request.send(res.encode())
            print("send is ok!!!!")

if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer((HOST, PORT), TCPhandler)
    server.serve_forever()

#下一步：从安卓上发送文件、接口并接收训练的数据文件并保存文件