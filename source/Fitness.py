#! python3
import csv
import random

from keras.models import Sequential
from keras.layers import LSTM, Activation, Dense, Dropout
from keras.optimizers import Adam
import numpy as np
import simplejson as json
import datetime
import copy
import keras
import numpy as np
from keras.models import load_model

import matplotlib.pyplot as plt
import operator
from functools import reduce

TIME_STEPS = 4
file_len = 0


def FileResolve(Filepath):
    # with open(Filepath, 'r') as load_f:

    click_info = CSVResolve(Filepath)
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
        cou_pressure = 0  #1秒钟内含有压力值的个数
        tot_pressure = 0  #总的压力值
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
        while End_click + 1 < len(click_info) and (
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
            ['Time', 'Start_x', 'Start_y', 'End_x', 'End_y', 'Avg_Pressure', 'Duration'], 0)
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

        operation_info.append(copy.deepcopy(one_operation))
        i = End_click + 1

    return operation_info


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
        operation = dict.fromkeys(['Time', 'x', 'y', 'pressure', 'total_seconds'], 0)
        operation['Time'] = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
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


# 最后返回的y_data是传递进去的参数y的值
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


class Classifier:
    def __init__(self, userid):

        self.model = Sequential()

        self.model.add(LSTM(TIME_STEPS * 6, input_shape=(TIME_STEPS, 6)))
        self.model.add(Dense(TIME_STEPS * 6 * 2))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(48, activation='sigmoid'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(2, activation='sigmoid'))

        adam = Adam(0.005)
        self.model.compile(optimizer=adam,
                           loss='categorical_crossentropy',
                           metrics=['accuracy'])
        self.model.load_weights("rnnmodel.h5")

        self.file_len = 4
        self.userid = userid

    def predict(self):
        res = 'a test'
        predic_data = FileResolve(self.userid + '.csv')
        n_len = len(predic_data)
        if n_len > self.file_len:
            tmp_x, tmp_y = DataReshape(predic_data, 0)
            res = self.model.predict_classes(np.reshape(reduce(operator.add, tmp_x), (len(tmp_x), TIME_STEPS, 6)))[-1]
            print("pre_res1", res)
            self.file_len = n_len
            if res == 0:
                print("success")
                return 'legal user'
            else:
                return 'illegal user'
        else:
            return 'data not enough'

    def test_model(self):
        self.model.predict(np.reshape([0] * 24, (1, 4, 6)))
        print("model test ok")
        return