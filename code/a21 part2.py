import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.polynomial import RankWarning
import pandas as pd
import math
import time

start = time.thread_time()

plt.axis("equal")
d = -0.1
data = list([])
for i in range(1, 5):
    data.append(np.array(pd.read_csv(
        f".\code\graph2{i}.csv", header=2)))  # 从csv文件获取数据
    plt.plot(data[i-1][:, 0], data[i-1][:, 1], '-o', color='b', markersize=1)

parent = np.array([[1, 3], [2, 2], [-1, 1], [2, 2]])


def unit(v):  # 单位化
    return(v/np.linalg.norm(v))


def inangle(v1, v2):  # 向量夹角
    return(math.acos(np.dot(v1, np.transpose(v2)) / (np.linalg.norm(v1)*np.linalg.norm(v2))))


def cross(v1, v2):
    return(v1[0]*v2[1]-v2[0]*v1[1])


def ifcross(p1, p2, q1, q2):
    v11 = q1-p1
    v12 = q2-p1
    v21 = q1-p2
    v22 = q2-p2
    if cross(v11, v12)*cross(v21, v22) < 0 and cross(v11, v21)*cross(v12, v22) < 0:
        return(1)
    else:
        return(0)


def drawborder(data):  # 内缩一次
    data = np.insert(data, data.shape[0], values=data[1, :], axis=0)
    data = np.insert(data, 0, values=data[data.shape[0]-3, :], axis=0)
    temp = np.array([0, 0])
    times = data.shape[0]-2
    i = 0
    while i < times:
        v1 = data[i+1, :]-data[i, :]
        v2 = data[i+2, :]-data[i+1, :]
        u = d/(math.sin(inangle(v1, v2)))
        if cross(v1, v2) > 0:
            new = data[i+1, :]+(unit(v2)-unit(v1))*u
        else:
            new = data[i+1, :]-(unit(v2)-unit(v1))*u
        temp = np.row_stack((temp, new))
        i += 1
    temp = np.delete(temp, 0, axis=0)
    i = 0
    while i < temp.shape[0]-3:
        j = i
        while j < temp.shape[0]-1:
            if ifcross(temp[i, :], temp[i+1, :], temp[j, :], temp[j+1, :]):
                temp = np.row_stack((temp[0:i, :], temp[j+1:, :]))
                continue
            else:
                j += 1
        i += 1
    return(temp)


def getint(data):  # 按精度离散化
    temp = new = np.array([0, 0.])
    for i in range(data.shape[0]-1):
        x1 = data[i, 0]
        y1 = data[i, 1]
        x2 = data[i+1, 0]
        y2 = data[i+1, 1]
        if x1 == x2:
            k = math.inf
        else:
            k = (y2-y1)/(x2-x1)  # 差分法
        if y1//abs(d) < y2//abs(d):
            for j in range(1, math.floor(y2//abs(d)-y1//abs(d)+1)):
                new[1] = round((y1//abs(d)+j)*abs(d), 1)
                new[0] = (new[1]-y1)/k+x1
                temp = np.row_stack((temp, new))
        else:
            if y1//abs(d) > y2//abs(d):
                for j in range(0, math.floor(y1//abs(d)-y2//abs(d))):
                    new[1] = round((y1//abs(d)-j)*abs(d), 1)
                    new[0] = (new[1]-y1)/k+x1
                    temp = np.row_stack((temp, new))
    temp = np.delete(temp, 0, axis=0)
    plt.plot(temp[:, 0], temp[:, 1], '-o', color='g', markersize=2)
    return(temp)


def findmax(data):
    index = np.array([], dtype='int64')
    for i in range(-1, data.shape[0]-1):
        if data[i, 1] > data[i-1, 1] and data[i, 1] >= data[i+1, 1]:
            index = np.append(index, [i], axis=0)
    return(index)


def findmin(data):
    index = np.array([], dtype='int64')
    for i in range(-1, data.shape[0]-1):
        if data[i, 1] <= data[i-1, 1] and data[i, 1] < data[i+1, 1]:
            index = np.append(index, [i], axis=0)
    return(index)


def findm(data):
    index = list([])
    for i in range(len(data)):
        index.append(np.array([findmax(data[i]), findmin(data[i])]))
    return(index)


def divideout(data_out, data_in, divide_in):
    ym = np.array([data_in[divide_in[0], 1],
                   data_in[divide_in[1], 1]])
    divide_out = np.array([], dtype='int16')
    for i in range(data_out.shape[0]):
        if data_out[i, 1] == ym[0] and data_out[i, 0] > data_in[divide_in[0], 0]:
            divide_out = np.append(divide_out, [i], axis=0)
            break
    for i in range(data_out.shape[0]):
        if data_out[i, 1] == ym[1] and data_out[i, 0] > data_in[divide_in[0], 0]:
            divide_out = np.append(divide_out, [i], axis=0)
            break
    return(divide_out)


def stackline(data_out, data_in, divide_out, divide_in):
    temp1 = np.row_stack(
        (data_out[:divide_out[0]+1], data_in[divide_in[0]:divide_in[1]+1], data_out[divide_out[1]:]))
    temp2 = np.row_stack(
        (data_in[:divide_in[0]], data_out[divide_out[0]+1:divide_out[1]], data_in[divide_in[1]+1:]))
    return(list([temp1, temp2]))


def divide1(data, index, parent):
    temp = list([])
    for i in range(1, (max(parent[:, 1]+1))//2+1):  # 填充 i 层
        for j in range(parent.shape[0]):  # 搜索 i 层的外边界
            if parent[j, 1] == 2*i-1:
                data_out = data[j]
                for k in range(parent.shape[0]):  # 搜索 j 作为外边界的对应内边界
                    if parent[k, 0] == j:
                        data_in = data[k]
                        divide_in = np.array(  # 内层分割点
                            [np.min(index[k][0, :]), np.max(index[k][1, :])])
                        divide_out = divideout(data_out,  # 外层分割点
                                               data_in, divide_in)
                        line = stackline(data_out, data_in,  # 交叉连接分割点
                                         divide_out, divide_in)
                        data_out = line[0]  # 更新外层
                        temp.append(line[1])  # 写入内层
                temp.append(data_out)  # 写入外层
    return(temp)


def divideline(data, index):
    line = np.array([0, 0])
    for n in [0, 1]:
        for i in index[n]:
            judge = 0
            j = i-2
            while j > -1:
                if data[j, 1] == data[i, 1]:
                    judge += 1
                    break
                j -= 1
            if judge == 0:
                continue
            k = i+2
            while k < data.shape[0]:
                if data[k, 1] == data[i, 1]:
                    judge += 1
                    break
                k += 1
            if judge == 1:
                continue
            elif n == 0:
                line = np.row_stack((line, [j, i]))
            else:
                line = np.row_stack((line, [i, k]))
    line = np.delete(line, 0, axis=0)
    return(line)


'''
def orderline(line):
    temp = np.array([0, 0, 0])
    while line.shape[0]:
        lowest = np.argmin(line[:, 0])
        temp = np.row_stack((temp, line[lowest]))
        line = np.delete(line, lowest, axis=0)
    temp = np.delete(temp, 0, axis=0)
    temp = np.delete(temp, 0, axis=1)
    temp = np.array(temp, dtype='int64')
    return(temp)
'''


def dividesub(data, line):
    temp = list([])
    while line.shape[0]:
        judge = 0
        for i in range(1, line.shape[0]):
            if line[0, 0] < line[i, 0] < line[0, 1]:
                line = np.row_stack((line[i, :], line))
                line = np.delete(line, i+1, axis=0)
                judge = 1
                break
        if judge == 0:
            temp.append(np.array(data[line[0, 0]+1:line[0, 1], :]))
            for j in range(line[0, 0]+1, line[0, 1]):
                data[j] = [0, 0]
            line = np.delete(line, 0, axis=0)
    temp.append(np.array(data[:, :]))
    for i in range(len(temp)):
        j = 0
        while j < temp[i].shape[0]:
            if temp[i][j, 0] == temp[i][j, 1] == 0:
                temp[i] = np.delete(temp[i], j, axis=0)
                continue
            j += 1
    return(temp)


def divide2(data, index):
    temp = list([])
    for i in range(len(data)):
        if index[i].shape[1] > 1:
            subdata = data[i]
            subtemp = list([])
            line = divideline(subdata, index[i])
            dividesub(subdata, line)

    return(temp)


for i in range(len(data)):
    data[i] = drawborder(data[i])
    data[i] = getint(data[i])
index = findm(data)  # 获取极值序号
data = divide1(data, index, parent)
index = findm(data)
data = divide2(data, index)


for i in range(len(data)):
    plt.plot(data[i][:, 0], data[i][:, 1], '-', color='r', markersize=1)


parent = np.array([[1, 3], [2, 2], [-1, 1], [2, 2]])  # [父级，层级]
plt.show()