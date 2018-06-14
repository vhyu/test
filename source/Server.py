#! python2
import socketserver
import source.classify_OCSVM as classfiy_OCS
#from keras.models import load_model
import time

cls = classfiy_OCS('test')
#cls.test_model()

class TCPhandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("\033[0;31m%s\033[0m" % "Connected by", self.client_address)
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
            print(time.strftime('%Y-%m-%d %H:%M:%S'), "file recv finished")
            # save file
            tfile = open(userid + '.csv', 'a+')
            tfile.write(file.decode())
            tfile.close()

            # get predict res
            # res = cls.predict()
            res= 'cla.predict_result'
            print("res:", "\033[0;31m%s\033[0m" % res)
            res = res + "\r\n"
            self.request.send(res.encode())


#host = '192.168.191.1'
host = '202.199.6.212'
port = 7780

if __name__ == '__main__':
    server = socketserver.ThreadingTCPServer((host, port), TCPhandler)
    server.serve_forever()