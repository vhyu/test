import math
import random
import matplotlib.pyplot as plt
import classify_OCSVM as cls


# 随机生成二进制编码
# chrom_length 的长度表示的是两个参数的二进制连接起来的长度
# 种群数量
def geneEncoding(pop_size, chrom_length):
    pop = []
    for i in range(pop_size):
        temp = []
        for j in range(chrom_length):
            temp.append(random.randint(0, 1))
        pop.append(temp)
    return pop[1:]


# 解码并计算值
# 解码
def decodechrom(pop, chrom_length, chrom_nu, chrom_gamma):
    temp = []  # 存储的是整个种群中的参数
    for i in range(len(pop)):
        t_nu = 0
        t_gamma = 0
        # 每一个t对应的是一个个体的参数
        t = []  # t表示的是一个数组，这个数组中的第一个元素是参数nu,第二个元素是参数gamma
        for j in range(chrom_length):
            tmp = pop[i][j]
            # 前10位表示的是nu的编码（0-9）
            if j < chrom_nu:
                t_nu += tmp * (math.pow(2, chrom_nu - 1 - j))
            # 后边的13位表示的gamma的编码(10-22)
            else:
                t_gamma += tmp * (math.pow(2, chrom_gamma - 1 - (j - chrom_nu)))
        t.append(t_nu)
        t.append(t_gamma)
        temp.append(t)
    return temp


# 计算预测值（将各个个体的基因其实就是那两个参数的编码，） 这个需要将我的适应度函数作为参数传进来
def calobjValue(pop, chrom_length, chrom_nu, chrom_gamma):
    obj_value = []
    temp_deco = decodechrom(pop, chrom_length, chrom_nu, chrom_gamma)
    for i in range(len(temp_deco)):  # temp1的长度和种群的个数是一致的
        # 得到的值需要进行处理在进行使用，要区分出nu和gamma
        # nu的范围是（0,1），对应的长度应该是：10^3*（1-（0）） = 1*10^3 =2^10
        # gamma的范围是（0，10）对应的长度应该是：10^3*（10-0） = 10^4 = 2^13
        the_nu = 0 + temp_deco[i][0] * ((1 - (0)) / (math.pow(2, chrom_nu) - 1))
        the_gamma = 0 + temp_deco[i][1] * ((10 - (0)) / (math.pow(2, chrom_gamma) - 1))
        obj_value.append(cls.rtn_error(the_nu, the_gamma))
    return obj_value


# 淘汰
def calfitValue(obj_value):
    fit_value = []
    c_min = 0.5
    for i in range(len(obj_value)):
        if obj_value[i] > c_min:
            temp = obj_value[i]
        else:
            temp = 0.0
        fit_value.append(temp)
    return fit_value


# 进行选择
def sum(fit_value):
    total = 0
    for i in range(len(fit_value)):
        total += fit_value[i]
    return total


def cumsum(fit_value):
    for i in range(len(fit_value) - 2, -1, -1):
        t = 0
        j = 0
        while (j <= i):
            t += fit_value[j]
            j += 1
        fit_value[i] = t
        fit_value[len(fit_value) - 1] = 1


def selection(pop, fit_value):
    newfit_value = []
    # 适应度总和
    total_fit = sum(fit_value)
    for i in range(len(fit_value)):
        newfit_value.append(fit_value[i] / total_fit)
        # 计算累计概率
    cumsum(newfit_value)
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
def crossover(pop, pc):
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
# 基因突变
def mutation(pop, pm):
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
# 找出最优解和最优解的基因编码
# 结果中best_individual存储的是最优的基因
# 结果中best_fit存储的是最优的适应度的值，也就是我的最优的准确率
def best(pop, fit_value):
    px = len(pop)
    best_individual = []
    best_fit = fit_value[0]
    for i in range(1, px):
        if (fit_value[i] > best_fit):
            best_fit = fit_value[i]
            best_individual = pop[i]
    return [best_individual, best_fit]


# 算法测试
# print
# 'y = 10 * math.sin(5 * x) + 7 * math.cos(4 * x)'
# 计算2进制序列代表的数值
#####需要变成自己的
def b2d(b, max_value, chrom_length):
    t = 0
    for j in range(len(b)):
        t += b[j] * (math.pow(2, j))
    t = t * max_value / (math.pow(2, chrom_length) - 1)
    return t


pop_size = 10  # 种群数量
max_value = 1024  # 基因中允许出现的最大值
chrom_length = 23  # 染色体长度（10+13）
chrom_nu = 10
chrom_gamma = 13
pc = 0.6  # 交配概率
pm = 0.2  # 变异概率
results = []  # 存储每一代的最优解，N个二元组
fit_value = []  # 个体适应度
fit_mean = []  # 平均适应度
num_Iterative = 15#迭代的次数

# pop = [[0, 1, 0, 1, 0, 1, 0, 1, 0, 1] for i in range(pop_size)]
pop = geneEncoding(pop_size, chrom_length)

#for的循环次数就是迭代的次数
# 迭代的次数，也就是选择最优解的次数
for i in range(num_Iterative):
    obj_value = calobjValue(pop, chrom_length, chrom_nu, chrom_gamma)  # 得到全部的个体评价
    fit_value = calfitValue(obj_value)  # 淘汰
    best_individual, best_fit = best(pop, fit_value)
    # 第一个存储最优的解, 第二个存储最优基因
    results.append([best_fit, b2d(best_individual, max_value, chrom_length)])
    selection(pop, fit_value)  # 新种群复制
    crossover(pop, pc)  # 交配
    mutation(pop, pm)  # 变异
    print ('第', i, '次迭代\n')

results = results[1:]
results.sort()

X = []
Y = []
for i in range(len(results)):
    X.append(i)
    t = results[i][0]
    Y.append(t)

plt.plot(X, Y)
plt.show()