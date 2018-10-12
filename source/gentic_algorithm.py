import math
import random
import matplotlib.pyplot as plt
from source.csvDataPrc import csvDataPrc as csvDP
from source.Class_fit import class_fit as cfit


# --------------------------随机生成二进制编码--------------------------
# chrom_length 的长度表示的是两个参数的二进制连接起来的长度
# 种群数量
class GA:
    # 得到的是一个数据集的dictionary
    myTrainCsvDP = []
    myTestCsvDP = []
    uId = ""
    pId = ""

    def __init__(self,trainD,testD,userId,pId):
        self.myTrainCsvDP = trainD
        self.myTestCsvDP = testD
        self.uId=userId
        self.pId=pId

    def geneEncoding(self,pop_size, chrom_length):
        pop = []
        for i in range(pop_size):
            temp = []
            for j in range(chrom_length):
                temp.append(random.randint(0, 1))
            pop.append(temp)
        return pop[1:]

    # 解码并计算值
    # 解码
    #--------------------------得到的是一个基因的解码--------------------------
    def oneDecodeChrom(self,individual,chrom_length,chrom_nu,chrom_gamma):
        one_decod_result =[]
        t_nu = 0
        t_gamma = 0
        for j in range(chrom_length):
            tmp = individual[j]
            # 前10位表示的是nu的编码（0-9）
            if j < chrom_nu:
                t_nu += tmp * (math.pow(2, chrom_nu - 1 - j))
            # 后边的13位表示的gamma的编码(10-22)
            else:
                t_gamma += tmp * (math.pow(2, chrom_gamma - 1 - (j - chrom_nu)))
        one_decod_result.append(t_nu)
        one_decod_result.append(t_gamma)
        return one_decod_result
    #pop存储的是种群
    #--------------------------得到的是整个种群的解码--------------------------
    def decodechrom(self,pop, chrom_length, chrom_nu, chrom_gamma):
        temp = []  # 存储的是整个种群中的参数
        for i in range(len(pop)):
            #  oneDecodeChrom()的返回值表示的是一个数组，这个数组中的第一个元素是参数nu,第二个元素是参数gamma
            temp.append(self.oneDecodeChrom(pop[i],chrom_length,chrom_nu,chrom_gamma))
        return temp

    #--------------------------讲一个基因的解码转换成需要的chrom_nu和chrom_gamma-------------
    def  indiviToCorS(self,deco_individual, chrom_nu,chrom_gamma):
        aNuGa = []
        the_nu = 0 + deco_individual[0] * ((1 - (0)) / (math.pow(2, chrom_nu) - 1))
        the_gamma = 0 + deco_individual[1] * ((10 - (0)) / (math.pow(2, chrom_gamma) - 1))
        if the_gamma == 0:
            the_gamma = 1/6#(numbers,averagePressure,startX,startY,endX,endY)
        aNuGa.append(the_nu)
        aNuGa.append(the_gamma)
        return aNuGa


    # --------------------------计算预测值（将各个个体的基因其实就是那两个参数的编码)-------------
    def calobjValue(self,pop, chrom_length, chrom_nu, chrom_gamma):
        obj_value = []
        temp_deco = self.decodechrom(pop, chrom_length, chrom_nu, chrom_gamma)
        for i in range(len(temp_deco)):  # temp1的长度和种群的个数是一致的
            # 得到的值需要进行处理在进行使用，要区分出nu和gamma
            # nu的范围是（0,1），对应的长度应该是：10^3*（1-（0）） = 1*10^3 =2^10
            # gamma的范围是（0，10）对应的长度应该是：10^3*（10-0） = 10^4 = 2^14
            the_nu = 0 + temp_deco[i][0] * ((1 - (0)) / (math.pow(2, chrom_nu) - 1))
            the_gamma = 0 + temp_deco[i][1] * ((10 - (0)) / (math.pow(2, chrom_gamma) - 1))
            if(the_nu == 0):
                the_nu = 0.0001
            if(the_gamma == 0):
                the_gamma = 0.0001
            cls_Fit = cfit(self.myTrainCsvDP,self.myTestCsvDP,self.uId,self.pId,the_nu,the_gamma)
            cls_Fit.fit()
            obj_value.append(cls_Fit.pred())


        return obj_value



    # --------------------------淘汰,筛选一下，将小于0.5准确率的个体的淘汰掉-------------
    def calfitValue(self,obj_value):
        fit_value = []
        c_min = 0.001
        for i in range(len(obj_value)):
            if obj_value[i] > c_min:
                temp = obj_value[i]
            else:
                temp = 0.001
            fit_value.append(temp)
        return fit_value


    # --------------------------进行选择--------------------------
    def sum(self,fit_value):
        total = 0
        for i in range(len(fit_value)):
            total += fit_value[i]
        return total


    def cumsum(self,fit_value):
        for i in range(len(fit_value) - 2, -1, -1):
            t = 0
            j = 0
            while (j <= i):
                t += fit_value[j]
                j += 1
            fit_value[i] = t
            fit_value[len(fit_value) - 1] = 1


    def selection(self,pop, fit_value):
        newfit_value = []
        # 适应度总和
        total_fit = sum(fit_value)
        for i in range(len(fit_value)):
            newfit_value.append(fit_value[i] / total_fit)
            # 计算累计概率
        self.cumsum(newfit_value)
        ms = []
        pop_len = len(pop)
        for i in range(pop_len):
            ms.append(random.random())
        ms.sort()
        fitin = 0
        newin = 0
        newpop = pop
        # 转轮盘选择法
        while newin < pop_len:
            if (ms[newin] < newfit_value[fitin]):
                newpop[newin] = pop[fitin]
                newin = newin + 1
            else:
                fitin = fitin + 1
        pop = newpop


    # 0.0 coding:utf-8 0.0

    # 交配
    def crossover(self,pop, pc):
        pop_len = len(pop)
        for i in range(pop_len - 1):
            if (random.random() < pc):
                cpoint = random.randint(0, len(pop[0]))
                temp1 = []
                temp2 = []
                temp1.extend(pop[i][0:cpoint])
                temp1.extend(pop[i + 1][cpoint:len(pop[i])])
                temp2.extend(pop[i + 1][0:cpoint])
                temp2.extend(pop[i][cpoint:len(pop[i])])
                pop[i] = temp1
                pop[i + 1] = temp2


    # 0.0 coding:utf-8 0.0
    # --------------------------基因突变--------------------------
    def mutation(self,pop, pm):
        px = len(pop)
        py = len(pop[0])

        for i in range(px):
            if (random.random() < pm):
                mpoint = random.randint(0, py - 1)
                if (pop[i][mpoint] == 1):
                    pop[i][mpoint] = 0
                else:
                    pop[i][mpoint] = 1


    # 0.0 coding:utf-8 0.0
    # -------------找出最优解和最优解的基因编码-------------
    # 结果中best_individual存储的是最优的基因
    # 结果中best_fit存储的是最优的适应度的值，也就是我的最优的准确率
    def best(self,pop, fit_value):
        px = len(pop)
        best_individual = pop[0]
        best_fit = fit_value[0]
        for i in range(1, px):
            if (fit_value[i] > best_fit):
                best_fit = fit_value[i]
                best_individual = pop[i]
        return [best_individual, best_fit]


    # 算法测试
    # print
    # 'y = 10 * math.sin(5 * x) + 7 * math.cos(4 * x)'
    # -------------计算2进制序列代表的数值-------------
    #####需要变成自己的
    def b2d(self,b, max_value, chrom_length):
        t = 0
        for j in range(len(b)):
            t += b[j] * (math.pow(2, j))
        t = t * max_value / (math.pow(2, chrom_length) - 1)
        return t

    #--------------调用模型以及预测-------------
    def fun_use(self):
        # case2：使用已经得到的模型
        # 测试保存的模型
        # 加载模型
        cls_Fit = cfit(self.myTrainCsvDP,self.myTestCsvDP,self.uId,self.pId)
        cls_Fit.loadM()
        print('使用已经保存的模型去训练得到的准确率：', cls_Fit.pred())


    #--------------训练以及保存模型-------------

    #psize 种群的大小
    #chrom_len 染色体长度
    #pmat 交配概率
    #pvar 变异概率
    #numIterative 迭代次数
    def funGA(self,psize,pmat,pvar,numItera):
        pop_size = psize  # 种群数量
        max_value = 10  # 基因中允许出现的最大值
        chrom_length = 24  # 染色体长度（10+13）
        chrom_nu = 10
        chrom_gamma = 14
        p_mat = pmat  # 交配概率
        p_var = pvar  # 变异概率
        results = []  # 存储每一代的最优解，N个二元组
        fit_value = []  # 个体适应度
        fit_mean = []  # 平均适应度
        num_Iterative = numItera#迭代的次数

        # pop = [[0, 1, 0, 1, 0, 1, 0, 1, 0, 1] for i in range(pop_size)]
        pop = self.geneEncoding(pop_size, chrom_length)

        X = []
        Y = []
        #训练模型以及保存
        #训练模型
        for i in range(num_Iterative):
            #找到本次迭代中这个种群中最好的个体
            #obj_value存储的是整个种群中每个个体的预测值
            obj_value = self.calobjValue(pop, chrom_length, chrom_nu, chrom_gamma)  # 得到全部的个体评价
            #fit_value存储的是种群中比较好的，大于0.5的
            fit_value = self.calfitValue(obj_value)  # 淘汰一部分个体
            # best_fit存储当前种群中的最优的解, best_individual存储最优基因
            best_individual, best_fit = self.best(pop, fit_value)
            #若没有找到最好的那么则忽略掉本次迭代的结果
            if(len(best_individual) != 0):
                results.append([best_fit, best_individual])
            # results.append([best_fit, b2d(best_individual, max_value, chrom_length)])
            self.selection(pop, fit_value)  # 新种群复制
            self.crossover(pop, p_mat)  # 交配
            self.mutation(pop, p_var)  # 变异
            # print('第',i,'次迭代中最好的准确率是：',best_fit,'最好的基因是：',best_individual)

        results = results[1:]
        # results.sort()
        fin_val_ind = results[results.index(max(results))]
        fin_deco = self.oneDecodeChrom(fin_val_ind[1], chrom_length, chrom_nu, chrom_gamma)
        fin_Nu_Ga = self.indiviToCorS(fin_deco,chrom_nu,chrom_gamma)
        print('迭代完成后最好的准确率是：',fin_val_ind[0],'最好的基因是：',
              fin_val_ind[1],'得到的最好的the_nu是：',fin_Nu_Ga[0],'the_gamma是：',fin_Nu_Ga[1])

        #保存模型
        #实例化一个对象
        cls_Fit = cfit(self.myTrainCsvDP, self.myTestCsvDP,self.uId,self.pId,fin_Nu_Ga[0], fin_Nu_Ga[1])
        #训练模型，得到一个clf
        #保存模型
        ####注意如果没有当前的目录，则不会自动创建目录
        cls_Fit.fit()
        cls_Fit.saveM()

        #画图
        for i in range(len(results)):
            X.append(i)
            t = results[i][0]
            Y.append(t)

        plt.plot(X, Y)
        plt.title(self.uId+"\\"+self.pId)
        plt.savefig('../Iterative200_pop100_pngs/'+self.uId+"_"+self.pId + '.png')
        # plt.hold('on')
        plt.show()
            #
            # 保存的一片空白，其实产生这个现象的原因很简单：
            # 在plt.show()后调用了plt.savefig() ，
            # 在plt.show()后实际上已经创建了一个新的空白的图片（坐标轴），
            # 这时候你再plt.savefig()就会保存这个新生成的空白图片。

    # funGA(50,0.5,0.6,50)
    # fun_use()