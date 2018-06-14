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

TIME_STEPS = 4
file_len = 0

# 合并一秒也就是视为一个动作的数据（number个点来构成）
def FileResolve(Filepath):
    # with open(Filepath, 'r') as load_f:

    click_info = CSVResolve(Filepath)
    # print('从CSV解析得到的数据：')
    # print(click_info)
    # print('click_info的size:', len(click_info))
    operation_info = []
    # test = test[1:]
    # for i in range(len(test)):
    #     one_click = json.JSONDecoder().decode('[' + test[i].split(']')[0] + ']')
    #     ope_info = JsonToOperation(one_click)
    #     if ope_info is None:
    #         continue
    #     else:
    #         click_info.append(ope_info)

    i = 0
    while i < len(click_info):  # 遍历所有点击操作
        Start_click = i
        End_click = i
        cou_pressure = 0
        tot_pressure = 0
        # major = 0
        # minor = 0
        if click_info[Start_click]['pressure'] > 0:  # 初始化平均压力，接触面
            cou_pressure = cou_pressure + 1
            tot_pressure = tot_pressure + click_info[Start_click]['pressure']
        # if click_info[Start_click]['major'] > 0:
        #     major = click_info[Start_click]['major']
        # if click_info[Start_click]['minor'] > 0:
        #     major = click_info[Start_click]['minor']

        # 合并操作
        while End_click + 1 < len(click_info) and (  # 由于下边这个操作，所以到值得到的duration一定是1，因为time这个字段是以秒为单位，现在需要的是获得毫秒就好了
                click_info[End_click + 1]['Time'] - click_info[Start_click]['Time']).total_seconds() <= 1:
            End_click = End_click + 1
            if End_click == len(click_info) - 1:
                break

            # if click_info[End_click]['major'] > 0:
            #     major = click_info[End_click]['major']
            # if click_info[End_click]['minor'] > 0:
            #     major = click_info[End_click]['minor']

            if click_info[End_click]['pressure'] > 0:
                cou_pressure = cou_pressure + 1
                tot_pressure = tot_pressure + click_info[End_click]['pressure']

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

        # if one_operation['Duration'] > 0:
        #     one_operation['Vector_x'] = (click_info[End_click]['x'] - click_info[Start_click]['x']) / one_operation[
        #         'Duration']
        #     one_operation['Vector_y'] = (click_info[End_click]['y'] - click_info[Start_click]['y']) / one_operation[
        #         'Duration']
        # else:
        #     one_operation['Vector_x'] = 0
        #     one_operation['Vector_y'] = 0
        if cou_pressure > 0:
            one_operation['Avg_Pressure'] = tot_pressure / cou_pressure
        else:
            one_operation['Avg_Pressure'] = 0
        one_operation['Numbers'] = End_click
        operation_info.append(copy.deepcopy(one_operation))
        i = End_click + 1

    return operation_info

# 找到这一条记录中的数据
def CSVResolve(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = [row for row in reader]

    click_info = []
    tmp = []
    for row in rows:
        if row != []:
            tmp.append(row)

    for row in rows:
        # 创建字典（区分APPID，其实就是进程的id）
        operation = dict.fromkeys(['Time', 'x', 'y', 'pressure', 'total_seconds','process_id'], 0)
        operation['Time'] = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
        operation['process_id'] = row[4]
        vali = 0
        if row[3] == 'ABS_MT_PRESSURE':
            operation['pressure'] = int(row[2])
            vali = 1
        elif row[3] == 'ABS_MT_POSITION_X':
            operation['x'] = int(row[2])
            vali = 1
        elif row[3] == 'ABS_MT_POSITION_Y':
            operation['y'] = int(row[2])
            vali = 1

        if vali:
            click_info.append(operation)
    return click_info

# 首先将一些值进行转换，归一化（x,y的坐标，平均压力）
# 将每一条记录存储在数组中
# 将数组转换成矩阵
def myDataReshap(operation_data):
    key = ['Avg_Pressure','Numbers','Start_x','End_y','Start_y','End_y']
    i = 0
    # trainData = []
    # while i < len(key):
    #     tmp = key[i]
    #     if (i<=1):
    #         num = [x[tmp] for x in operation_data]
    #         j = 0
    #         if (max(num) - min(num)) != 0:
    #             for j in range(len(operation_data)):
    #                 trainData[i].append((operation_data[j][tmp] - min(num)) / (max(num) - min(num)))
    #         else:
    #             for j in range(len(operation_data)):
    #                 trainData[i].append(0)
    #     if(2<=i<=3):
    #         j= 0
    #         for j in range(len(operation_data)):
    #             trainData[i].append(operation_data[j]['Start_x'] / 1080)
    #             trainData[i].append(operation_data[j]['End_x'] / 1080)
    #     else:
    #         j=0
    #         for j in range(len(operation_data)):
    #             trainData[i].append(operation_data[j]['Start_y'] / 1780)
    #             trainData[i].append(operation_data[j]['End_y'] / 1780)

    # 相同的功能
    # 得到record中的number（归一化）
    Numbers = []
    num_N = [x['Numbers'] for x in operation_data]
    # print(num_N)
    # print(len(operation_data))
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

    return trainData

# 我的情况不需要这样
def DataReshape(csv_data, y, TIME_STEPS=4):
    x_data = []
    y_data = []
    key = ['Avg_Pressure']
    for k in key:
        num = [x[k] for x in csv_data]
        if (max(num) - min(num)) != 0:
            for i in range(len(csv_data)):
                csv_data[i][k] = (csv_data[i][k] - min(num)) / (max(num) - min(num))
        else:
            for i in range(len(csv_data)):
                csv_data[i][k] = 0

    key = ['Start_x', 'End_x']
    for k in key:
        for i in range(len(csv_data)):
            csv_data[i][k] = csv_data[i][k] / 1080

    key = ['Start_y', 'End_y']
    for k in key:
        for i in range(len(csv_data)):
            csv_data[i][k] = csv_data[i][k] / 1788

    tmp = []
    for i in csv_data:
        tmp.append(
            [i['Duration'], i['Start_x'], i['Start_y'], i['End_x'], i['End_y'], i['Avg_Pressure']])

    for i in range(0, len(tmp) - TIME_STEPS):
        one_time = []
        for j in range(0, TIME_STEPS):
            one_time.append(tmp[i + j])
        x_data.append(one_time)
        y_data.append(y)

    return x_data, y_data

# class Classfy:
#    def __init__(self, userid):
#        self.userid = 12
#    def predict(self):
#            return 'data not enough'

# xx, yy = np.meshgrid(np.linspace(-5, 5, 500), np.linspace(-5, 5, 500))



#
# operinfo = FileResolve('train.csv')
# trainD = myDataReshap(operinfo)
# clf = svm.OneClassSVM(nu=0.03, kernel="rbf", gamma=4)
# clf.fit(trainD)
# testD = myDataReshap(FileResolve('my_Test.csv'))
# y_pred_test = clf.predict(trainD)
# n_error_test = y_pred_test[y_pred_test == -1].size
# print(1-n_error_test/len(operinfo))


def rtn_error(the_nu,the_gamma):
    # 获取训练集
    operinfo = FileResolve('../data/train.csv')
    trainD = myDataReshap(operinfo)
    # print('\n训练集的大小:',len(trainD))
    # print (trainD)
    clf = svm.OneClassSVM(nu=the_nu, kernel="rbf", gamma=the_gamma)
    clf.fit(trainD)
    testD = myDataReshap(FileResolve('../data/my_Test.csv'))
    # print('\n测试集的大小:',len(testD))
    y_pred_test = clf.predict(testD)
    n_error_test = y_pred_test[y_pred_test == -1].size
    return 1-n_error_test/len(operinfo)

# Generate train data
# X = 0.3 * np.random.randn(100, 6)
# X_train = np.r_[X + 2, X - 2, X, X - 1, X + 1, X * 0.8 + 2]

# # 获取训练集
# operinfo = FileResolve('.csv')
# # print('从fileResolve 函数得到的字典数组是:', operinfo)
# print(operinfo)
# trainD = myDataReshap(operinfo)
# print(trainD)
# print('从MydataReshape 函数得到的矩阵是:', trainD)

# # 最后返回的yy的值是传递进去的第二个参数的值,但是好像没有是什么用处
# xx,yy = DataReshape(openinfo,0)
# print('得到的三维数组：xx的value是',xx)

# 从csv文件中读取数据到矩阵中 delimiter,分隔符，skiprows，开始的行数
# my_matrix = np.loadtxt(open(".csv","rb"),delimiter=",",skiprows=0)
# print(my_matrix)
# csv_reader = csv.reader(open('test.csv', encoding='utf-8'))
# for row in csv_reader:
#     print(row)



# my_Test = trainD
# dim = len(my_Test[0])
#
# # Generate some regular novel observations
# X = 0.3 * np.random.randn(20, dim)
# X_test = np.r_[X + 2, X - 2, X, X - 1, X + 1, X * 0.8 + 2]
# # Generate some abnormal novel observations
# X_outliers = np.random.uniform(low=-4, high=4, size=(20, 6))
#
# # fit the model
# clf = svm.OneClassSVM(nu=0.005, kernel="rbf", gamma=2)
# clf.fit(my_Test)
# y_pred_train = clf.predict(my_Test)
# y_pred_test = clf.predict(my_Test)
# y_pred_outliers = clf.predict(X_outliers)
# n_error_train = y_pred_train[y_pred_train == -1].size
# n_error_test = y_pred_test[y_pred_test == -1].size
# n_error_outliers = y_pred_outliers[y_pred_outliers == 1].size
#
# # plot the line, the points, and the nearest vectors to the plane
# # Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
# # Z = Z.reshape(xx.shape)
#
# # plt.title("Novelty Detection")
# # plt.contourf(xx, yy, Z, levels=np.linspace(Z.min(), 0, 7), cmap=plt.cm.PuBu)
# # a = plt.contour(xx, yy, Z, levels=[0], linewidths=2, colors='darkred')
# # plt.contourf(xx, yy, Z, levels=[0, Z.max()], colors='palevioletred')
#
# # s = 40
# # b1 = plt.scatter(X_train[:, 0], X_train[:, 1], c='white', s=s)
# # b2 = plt.scatter(X_test[:, 0], X_test[:, 1], c='blueviolet', s=s)
# # c = plt.scatter(X_outliers[:, 0], X_outliers[:, 1], c='gold', s=s)
# # plt.axis('tight')
# # plt.xlim((-5, 5))
# # plt.ylim((-5, 5))
# # plt.legend([a.collections[0], b1, b2, c],
# #          ["learned frontier", "training observations",
# #            "new regular observations", "new abnormal observations"],
# #           loc="upper left",
# #           prop=matplotlib.font_manager.FontProperties(size=11))
# # plt.xlabel(
# #    "error train: %d/200 ; errors novel regular: %d/40 ; "
# #    "errors novel abnormal: %d/40"
# #    % (n_error_train, n_error_test, n_error_outliers))
# # plt.show()
# print('error train: ', n_error_train /len(operinfo), 'errors novel regular:', n_error_test / len(operinfo), 'errors novel abnormal: ',
#       n_error_outliers / len(operinfo))