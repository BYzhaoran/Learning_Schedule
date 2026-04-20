# NumPy & Matplotlib.pyplot 常用函数速查

## NumPy 常用函数

### 数组创建
| 函数 | 说明 | 示例 |
|------|------|------|
| `np.array()` | 创建数组 | `np.array([1, 2, 3])` |
| `np.zeros()` | 创建全0数组 | `np.zeros((3, 3))` |
| `np.ones()` | 创建全1数组 | `np.ones((2, 4))` |
| `np.arange()` | 创建等差数列 | `np.arange(0, 10, 2)` → [0,2,4,6,8] |
| `np.linspace()` | 均匀分布的数组 | `np.linspace(0, 1, 5)` → 5个点从0到1 |
| `np.random.rand()` | 随机数[0,1) | `np.random.rand(3, 3)` |
| `np.random.randn()` | 标准正态分布 | `np.random.randn(3, 3)` |
| `np.random.randint()` | 随机整数 | `np.random.randint(0, 10, 5)` |

### 数组操作
| 函数 | 说明 | 示例 |
|------|------|------|
| `shape` | 获取数组形状 | `arr.shape` |
| `reshape()` | 改变数组形状 | `arr.reshape(2, 3)` |
| `flatten()` | 展平为1D数组 | `arr.flatten()` |
| `T` | 转置 | `arr.T` |
| `sort()` | 排序 | `np.sort(arr)` |
| `argsort()` | 排序索引 | `np.argsort(arr)` |

### 数学函数
| 函数 | 说明 | 示例 |
|------|------|------|
| `mean()` | 求平均值 | `np.mean(arr)` |
| `std()` | 求标准差 | `np.std(arr)` |
| `var()` | 求方差 | `np.var(arr)` |
| `sum()` | 求和 | `np.sum(arr)` |
| `max()` / `min()` | 最大/最小值 | `np.max(arr)` |
| `sqrt()` | 平方根 | `np.sqrt(arr)` |
| `exp()` | 指数函数 | `np.exp(arr)` |
| `log()` | 自然对数 | `np.log(arr)` |
| `sin()`, `cos()` | 三角函数 | `np.sin(arr)` |

### 线性代数
| 函数 | 说明 | 示例 |
|------|------|------|
| `dot()` | 矩阵乘法/向量点积 | `np.dot(A, B)` |
| `linalg.inv()` | 矩阵求逆 | `np.linalg.inv(A)` |
| `linalg.solve()` | 求解线性方程组 | `np.linalg.solve(A, b)` |

### 其他常用
| 函数 | 说明 | 示例 |
|------|------|------|
| `concatenate()` | 连接数组 | `np.concatenate([a, b])` |
| `stack()` | 堆叠数组 | `np.stack([a, b])` |
| `split()` | 分割数组 | `np.split(arr, 3)` |
| `where()` | 条件选择 | `np.where(arr > 5, 1, 0)` |
| `random.seed()` | 设置随机种子 | `np.random.seed(89)` |

---

## Matplotlib.pyplot 常用函数

### 基础绘图
| 函数 | 说明 | 示例 |
|------|------|------|
| `plot()` | 线性图 | `plt.plot(x, y)` |
| `scatter()` | 散点图 | `plt.scatter(x, y)` |
| `bar()` | 柱状图 | `plt.bar(x, y)` |
| `hist()` | 直方图 | `plt.hist(data, bins=20)` |
| `pie()` | 饼图 | `plt.pie(data, labels=labels)` |

### 图表元素
| 函数 | 说明 | 示例 |
|------|------|------|
| `title()` | 设置标题 | `plt.title('Title')` |
| `xlabel()` | X轴标签 | `plt.xlabel('X Label')` |
| `ylabel()` | Y轴标签 | `plt.ylabel('Y Label')` |
| `legend()` | 添加图例 | `plt.legend()` |
| `grid()` | 显示网格 | `plt.grid(True)` |
| `xlim()` / `ylim()` | 设置坐标轴范围 | `plt.xlim(0, 10)` |

### 样式与颜色
| 函数/参数 | 说明 | 示例 |
|------|------|------|
| `color` | 颜色 | `plt.plot(x, y, color='red')` |
| `linestyle` | 线型 | `plt.plot(x, y, linestyle='--')` |
| `marker` | 标记点 | `plt.plot(x, y, marker='o')` |
| `linewidth` | 线宽 | `plt.plot(x, y, linewidth=2)` |
| `alpha` | 透明度 | `plt.plot(x, y, alpha=0.5)` |

### 图窗管理
| 函数 | 说明 | 示例 |
|------|------|------|
| `figure()` | 创建新图窗 | `plt.figure(figsize=(10, 6))` |
| `subplot()` | 创建子图 | `plt.subplot(2, 2, 1)` |
| `show()` | 显示图表 | `plt.show()` |
| `savefig()` | 保存图表 | `plt.savefig('fig.png')` |
| `close()` | 关闭图窗 | `plt.close()` |

### 常用参数速查
```python
# 线型 linestyle
'-'    # 实线
'--'   # 虚线
'-.'   # 点划线
':'    # 点线

# 标记点 marker
'o'    # 圆形
's'    # 正方形
'^'    # 三角形
'x'    # X标记
'+'    # 加号
'.'    # 点

# 颜色 color
'r'    # 红色
'g'    # 绿色
'b'    # 蓝色
'k'    # 黑色
'w'    # 白色
'y'    # 黄色
'c'    # 青色
'm'    # 洋红色
```

---

## 快速示例

### NumPy 基础操作
```python
import numpy as np

# 创建和操作
x = np.random.rand(10)
x_sorted = np.sort(x)
x_normalized = (x - np.mean(x)) / np.std(x)

# 矩阵操作
A = np.array([[1, 2], [3, 4]])
b = np.array([5, 6])
x = np.linalg.solve(A, b)  # 解 Ax = b
```

### Matplotlib 基础绘图
```python
import matplotlib.pyplot as plt

# 创建图表
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'r--', linewidth=2, label='Fitted Line')
plt.scatter(x_data, y_data, marker='o', label='Data Points')
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Linear Regression')
plt.legend()
plt.grid(True)
plt.show()
```
