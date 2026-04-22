import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

def Real_fun(x) :
    return 1.35 * x + 0.25

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


'''

### package
numpy
matplotlib
sklearn

### 关键函数

```
np.linspace(始, 末, 量)
生成均匀分布数组。

plt.plot(横坐标, 对应纵坐标, label)
绘制曲线。

plt.legend(loc="best")
显示图例, 并自动选择尽量不遮挡曲线的位置。

plt.show()
展示图像。

LinearRegression().fit(X, y)
用输入特征 X 和目标值 y 拟合模型参数。

X_train_data.reshape(-1, 1)
将一维数组转为二维列向量, 满足 sklearn 的 X 输入要求: (样本数, 特征数)。

LinearRegression().predict(X_test[:, np.newaxis])
根据输入 X_test 预测 y。

model.coef_[0][0]
模型斜率 (单特征、单输出时)。

model.intercept_[0]
模型截距 (单输出时)。
```



'''