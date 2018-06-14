#! python3
import random
from sklearn import svm
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager
import csv
import sys
# from keras.models import Sequential
# from keras.layers import LSTM, Activation, Dense, Dropout
# from keras.optimizers import Adam
import simplejson as json
import datetime
import copy
# import keras
# from keras.models import load_model

import matplotlib.pyplot as plt
import operator
from functools import reduce

from sklearn.externals import joblib

TIME_STEPS = 4
file_len = 0

class Classify_OCSVM:

    def FileResolve(self,Filepath):# 合并一秒也就是视为一个动作的数据（number个点来构成）
        # with open(Filepath, 'r') as load_f:

        pid_clicks_dic = self.CSVResolve(Filepath)
        pid_opers_dic = dict.fromkeys(pid_clicks_dic.keys(),0)
        for key in pid_clicks_dic:
            click_info = pid_clicks_dic[key]
            operation_info = []
            i = 0
            while i < len(click_info):  # 遍历每一个pid中的所有点击操作
                Start_click = i
                End_click = i
                cou_pressure = 0
                tot_pressure = 0
                # major = 0
                # minor = 0
                if click_info[Start_click]['pressure'] > 0:  # 初始化平均压力，接触面
                    cou_pressure = cou_pressure + 1
                    tot_pressure = tot_pressure + click_info[Start_click]['pressure']
                # 合并操作
                while End_click + 1 < len(click_info) and (  # 由于下边这个操作，所以到值得到的duration一定是1，因为time这个字段是以秒为单位，现在需要的是获得毫秒就好了
                        click_info[End_click + 1]['Time'] - click_info[Start_click]['Time']).total_seconds() <= 1:
                    End_click = End_click + 1
                    if End_click == len(click_info) - 1:
                        break

                    if click_info[End_click]['pressure'] > 0:
                        cou_pressure = cou_pressure + 1
                        tot_pressure = tot_pressure + click_info[End_click]['pressure']

                #one_operation表示一个操作的数据信息
                one_operation = dict.fromkeys(
                    ['Time', 'Start_x', 'Start_y', 'End_x', 'End_y', 'Avg_Pressure', 'Duration', 'numbers'], 0)
                one_operation['Duration'] = (
                        click_info[End_click]['Time'] - click_info[Start_click]['Time']).total_seconds()
                one_operation['Time'] = click_info[Start_click]['Time']
                for k in range(Start_click, End_click):
                    if click_info[k]['x'] != 0:
                        one_operation['Start_x'] = click_info[k]['x']
                        break
                for k in range(Start_click, End_click):
                    if click_info[k]['y'] != 0:
                        one_operation['Start_y'] = click_info[k]['y']
                        break

                for k in range(End_click, Start_click, -1):
                    if click_info[k]['x'] != 0:
                        one_operation['End_x'] = click_info[k]['x']
                        break

                for k in range(End_click, Start_click, -1):
                    if click_info[k]['y'] != 0:
                        one_operation['End_y'] = click_info[k]['y']
                        break

                if cou_pressure > 0:
                    one_operation['Avg_Pressure'] = tot_pressure / cou_pressure
                else:
                    one_operation['Avg_Pressure'] = 0
                one_operation['Numbers'] = End_click
                #operation_info 表示的是一个pid中对应的所有的operation的集合
                operation_info.append(copy.deepcopy(one_operation))
                i = End_click + 1
            #得到每一个pid对应的one_operation(也就是得到每一个pid对应的不同的操作)
            #返回的是一个关于操作们的数组
            pid_opers_dic[key] = operation_info
        return pid_opers_dic

    # 找到这一条记录中的数据
    def CSVResolve(self,filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = [row for row in reader]

        clicks_info = []
        # tmp = []
        # for row in rows:
        #     if row != []:
        #         tmp.append(row)

        last_PID = rows[0][4]
        pid_values = []
        pid_values.append(last_PID)
        for row in rows:
            # 创建字典（区分APPID，其实就是进程的id）
            aClick = dict.fromkeys(['Time', 'x', 'y', 'pressure', 'total_seconds','process_id'], 0)
            aClick['Time'] = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
            vali = 0
            if row[4] not in pid_values:
                pid_values.append(row[4])

            aClick['process_id'] = row[4]

            if row[3] == 'ABS_MT_PRESSURE':
                aClick['pressure'] = int(row[2])
                vali = 1
            elif row[3] == 'ABS_MT_POSITION_X':
                aClick['x'] = int(row[2])
                vali = 1
            elif row[3] == 'ABS_MT_POSITION_Y':
                aClick['y'] = int(row[2])
                vali = 1

            if vali:
                clicks_info.append(aClick)

            #last_PID存储上一条记录的ProcessID
            last_PID = row[4]


        pids_dics = dict.fromkeys(pid_values,0)

        for key in pids_dics:
            tmp_pid_dic = []
            for i in range(len(clicks_info)):
                if clicks_info[i]['process_id'] == key:
                    tmp_pid_dic.append(copy.deepcopy(clicks_info[i]))
            pids_dics[key] = tmp_pid_dic

        return pids_dics

    # 首先将一些值进行转换，归一化（x,y的坐标，平均压力）
    # 将每一条记录存储在数组中
    # 将数组转换成矩阵
    def myDataReshap(self,dic_operas):

        pid_trainData_dic = dict.fromkeys(dic_operas.keys())
        for key in dic_operas:
            operation_data = dic_operas[key]
            # 得到record中的number（归一化）
            Numbers = []
            num_N = [x['Numbers'] for x in operation_data]

            if (max(num_N) - min(num_N)) != 0:
                for i in range(len(operation_data)):
                    Numbers.append((operation_data[i]['Numbers'] - min(num_N)) / (max(num_N) - min(num_N)))
            else:
                for i in range(len(operation_data)):
                    Numbers.append(0)

            # 得到record中的pressure（归一化）
            pre = []
            num_P = [x['Avg_Pressure'] for x in operation_data]
            if (max(num_P) - min(num_P)) != 0:
                for i in range(len(operation_data)):
                    pre.append((operation_data[i]['Avg_Pressure'] - min(num_P)) / (max(num_P) - min(num_P)))
            else:
                for i in range(len(operation_data)):
                    pre.append(0)

            # 得到record中的x（与屏幕进行比例运算）注意需要获取到屏幕的大小，不应该设定
            sx = []
            sy = []
            ex = []
            ey = []
            for i in range(len(operation_data)):
                sx.append(operation_data[i]['Start_x'] / 1080)
                ex.append(operation_data[i]['End_x'] / 1080)

            for i in range(len(operation_data)):
                sy.append(operation_data[i]['Start_y'] / 1788)
                ey.append(operation_data[i]['End_y'] / 1788)

            trainData = []
            for i in range(len(operation_data)):
                trainData.append([Numbers[i], pre[i], sx[i], sy[i], ex[i], ey[i]])
            pid_trainData_dic[key] = trainData

        return pid_trainData_dic

    def rtn_error(self,the_nu,the_gamma):
        # 获取训练集
        operinfo = self.FileResolve('../data/train.csv')
        trainD_dic = self.myDataReshap(operinfo)

        for key in trainD_dic:
            clf = svm.OneClassSVM(nu=the_nu, kernel="rbf", gamma=the_gamma)
            #训练
            clf.fit(trainD_dic[key])
            module_Name = '../modle/'+ key+"_model.m"
            #保存
            joblib.dump(clf, module_Name)

        testD_dic = self.myDataReshap(self.FileResolve('../data/my_Test.csv'))
        pre_Res_dic = dict.fromkeys(testD_dic.keys(),0)
        for key in testD_dic:
            testD_dic[key]
            #从文件中读取模型进行预测
            module_Name = '../modle/'+key+"_model.m"
            clf = joblib.load(module_Name)
            #进行预测
            y_pred_test = clf.predict(testD_dic[key])

            #预测结果
            n_error_test = y_pred_test[y_pred_test == -1].size
            print('\n错误的个数:',n_error_test,'总的个数：',len(testD_dic[key]),'准确率的结果是:',1-(n_error_test/len(testD_dic[key])))
            pre_Res_dic[key] = 1-(n_error_test/len(testD_dic[key]))
        return pre_Res_dic

if __name__ == '__main__':

    cls_OCSVM = Classify_OCSVM()
    print(cls_OCSVM.rtn_error(0.03,4))