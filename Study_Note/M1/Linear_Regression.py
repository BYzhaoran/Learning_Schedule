import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

def Real_fun(x) :
    return 1.35 * x**2 + 0.25

np.random.seed(89)  # 设置随机种子
n_data_num = 3000    # 设置采样数据点的个数

X_train_data = np.sort(np.random.rand(n_data_num))
y_train_data = (Real_fun(X_train_data) + np.random.randn(n_data_num) * 0.05).reshape(n_data_num, 1)
model = LinearRegression()
model.fit(X_train_data.reshape(-1, 1), y_train_data)
print("模型的斜率（系数）:", model.coef_[0][0])
print("模型的截距:", model.intercept_[0])

X_test = np.linspace(0, 1, 100)
plt.plot(X_test, model.predict(X_test[:, np.newaxis]), label="Model")
plt.plot(X_test, Real_fun(X_test), label="True function")
# plt.scatter(X_train_data, y_train_data)  # 画出训练集的点
plt.legend(loc="best")
plt.show()