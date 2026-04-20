import numpy as np
import matplotlib.pyplot as plt

def Real_fun(x) :
    return 1.35 * x + 0.25

np.random.seed(89)  # 设置随机种子
n_data_num = 30     # 设置采样数据点的个数

X_train_data = np.sort(np.random.rand(n_data_num))
y_train_data = (Real_fun(X_train_data) + np.random.randn(n_data_num) * 0.05).reshape(n_data_num, 1)