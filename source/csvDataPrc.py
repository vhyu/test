import csv
import copy
import datetime

class csvDataPrc():
    csvFilePath = ''
    csvR = [] #csv文件经过处理得到，一个点击数据的dic,dic用pid作为其key值
    fileR = [] #csvR信息经过处理得到,一个动作数据的dic
    dataR = [] #fileR信息经过处理得到，一个归一化后的数据集的dic
    def __init__(self,the_FP):
        self.csvFilePath = the_FP

    def sub(self,string, p, c):
        new = []
        for s in string:
            new.append(s)
        new[p] = c
        return ''.join(new)

    #读取csv文件，并将每一行的数据进行处理，得到的是点击信息的集合，其实并不是存储店的信息，只是为了过滤掉不是event1的那些事件
    def CSVResolve(self):
        with open(self.csvFilePath, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = [row for row in reader]

        clicks_info = []
        for row in rows:
            # 创建字典
            aClick = dict.fromkeys(['Time', 'x', 'y', 'pressure', 'total_seconds', 'process_id','event_type','fingers'], 0)
            strTime = self.sub(row[1],19,'.')
            aClick['Time'] = datetime.datetime.strptime(strTime, "%Y-%m-%d %H:%M:%S.%f")
            vali = 0
            aClick['fingers'] = 0
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
            elif row[3] == 'BTN_TOOL_FINGER':
                aClick['event_type'] = row[2]
                vali=1
            elif row[3] == 'ABS_MT_SLOT':
                aClick['fingers'] = 1
            if vali:
                clicks_info.append(aClick)
        self.csvR = clicks_info

    #将从csv中读取到的点击信息的dic数组进行处理
    #得到的是每一个动作的数据的集合
    #返回的是一个dictionary，键对应的是pid,值对应的是数组，每一个数组是operation的集合
    def FileResolve(self):  # 合并一秒也就是视为一个动作的数据（number个点来构成）
        click_info = self.csvR
        operation_info = []
        i = 0
        while i < len(click_info)-1:  # 遍历每一个pid中的所有点击操作
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
            # while End_click + 1 < len(click_info) and (  # 由于下边这个操作，所以到值得到的duration一定是1，因为time这个字段是以秒为单位，现在需要的是获得毫秒就好了
            #     click_info[End_click + 1]['Time'] - click_info[Start_click]['Time']).total_seconds() <= 1:
            # 现在获取到的就是毫秒级的
            # 由于下边这个操作，所以到值得到的duration一定是1，因为time这个字段是以秒为单位，现在需要的是获得毫秒就好了
            # while End_click + 1 < len(click_info) and (click_info[End_click + 1]['event_type'] == "UP" and click_info[Start_click]['btn_tool_finger']=="DOWN"):
            while End_click + 1 < len(click_info) and (click_info[End_click + 1]['event_type'] == "UP" and click_info[Start_click]['event_type']=="DOWN"):
                End_click = End_click + 1
                if End_click == len(click_info) - 1:
                    break

                if click_info[End_click]['pressure'] > 0:
                    cou_pressure = cou_pressure + 1
                    tot_pressure = tot_pressure + click_info[End_click]['pressure']

            # one_operation表示一个操作的数据信息
            one_operation = dict.fromkeys(
                    ['Time', 'Start_x', 'Start_y', 'End_x', 'End_y', 'Avg_Pressure', 'Duration', 'Numbers', 'Fingers'], 0)
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
            one_operation['Fingers'] = click_info[Start_click]['fingers']
            # operation_info 表示的是一个pid中对应的所有的operation的集合
            operation_info.append(copy.deepcopy(one_operation))
            i = End_click + 1
            # 得到每一个pid对应的one_operation(也就是得到每一个pid对应的不同的操作)
            # 返回的是一个关于操作们的数组
        self.fileR = operation_info

        # 找到这一条记录中的数据

        # 首先将一些值进行转换，归一化（x,y的坐标，平均压力）
        # 将每一条记录存储在数组中
        # 将数组转换成矩阵
    def DataReshap(self):
        operation_data = self.fileR
        # 得到record中的number（归一化）
        Numbers = []
        num_N = [x['Numbers'] for x in operation_data]

        # num_N为空的情况是什么样的，不知道？？？
        if not num_N:
            num_N = [1, 1, 1]
            # print("num_N is empty")

        if (max(num_N) - min(num_N)) != 0:
            for i in range(len(operation_data)):
                Numbers.append((operation_data[i]['Numbers'] - min(num_N)) / (max(num_N) - min(num_N)))
        else:
            for i in range(len(operation_data)):
                Numbers.append(0)

        # 得到record中的pressure（归一化）
        pre = []
        num_P = [x['Avg_Pressure'] for x in operation_data]
        # num_P为空的情况是什么样的，不知道？？？与num_N是对应的
        if not num_P:
            num_P = [1, 1, 1]
            # print("num_N is empty")

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
        self.dataR = trainData

    def set(self):
        self.CSVResolve()
        self.FileResolve()
        self.DataReshap()
        return self.dataR#返回的是一个可以进行训练的数据集