import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
import os
import importlib.util


# 解析 MNIST 原始数据目录。
# 目标：无论脚本从哪个工作目录启动，都能找到正确的数据位置。
# 返回值：包含 load_data.py 与 4 个 .gz 数据文件的目录绝对路径。
def resolve_mnist_raw_dir():
    # 当前脚本所在目录：.../Study_Note/M1
    current_dir = os.path.dirname(__file__)
    # 仓库根目录（从当前脚本向上三级）：.../Learning_Schedule
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    # 依次尝试候选路径。
    # 1) 当前目录下的数据目录（当前项目结构实际使用的位置）
    # 2) 仓库根目录下的数据目录（兼容其它可能布局）
    candidates = [
        os.path.join(current_dir, "datasets", "MNIST", "raw"),
        os.path.join(repo_root, "datasets", "MNIST", "raw"),
    ]

    # 判定“目录可用”所需的关键文件。
    # 同时检查读取脚本 + 训练集/测试集的图像与标签文件，避免只找到空目录。
    required_files = [
        "train-images-idx3-ubyte.gz",
        "train-labels-idx1-ubyte.gz",
        "t10k-images-idx3-ubyte.gz",
        "t10k-labels-idx1-ubyte.gz",
        "load_data.py",
    ]

    # 按顺序遍历候选目录，找到第一个满足全部文件存在的目录后立即返回。
    for path in candidates:
        if all(os.path.exists(os.path.join(path, name)) for name in required_files):
            return path

    # 全部候选目录都不满足时，抛出详细异常，提示实际检查过的路径，便于快速排查。
    raise FileNotFoundError(
        "MNIST raw data directory not found. Checked: " + ", ".join(candidates)
    )


# 从本地加载MNIST数据集
def load_mnist_data():
    # 先解析真实可用的数据目录，避免硬编码路径导致 FileNotFoundError。
    DATA_Base_path = resolve_mnist_raw_dir()

    # load_data.py 位于 MNIST/raw 目录，里面定义了 load_local_mnist。
    load_data_path = os.path.join(DATA_Base_path, "load_data.py")

    # 通过文件路径动态导入模块：
    # - 不依赖项目是否被识别为 Python package
    # - 不依赖运行时 PYTHONPATH
    # - 脚本单独执行也能稳定导入
    spec = importlib.util.spec_from_file_location("mnist_load_data", load_data_path)

    # 导入规格为空通常意味着文件路径无效或 loader 初始化失败。
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import load_local_mnist from {load_data_path}")

    # 根据 spec 创建模块对象并执行模块代码，获得其中定义的函数。
    mnist_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mnist_module)
    load_local_mnist = mnist_module.load_local_mnist

    # 读取本地 MNIST。
    # normalize=True：将像素缩放到 [0, 1]。
    # one_hot=False：标签保持整数类别（0-9），适配 sklearn 分类器接口。
    (X_train, y_train), (X_test, y_test) = load_local_mnist(
        x_train_path=os.path.join(DATA_Base_path, 'train-images-idx3-ubyte.gz'),
        y_train_path=os.path.join(DATA_Base_path, 'train-labels-idx1-ubyte.gz'),
        x_test_path=os.path.join(DATA_Base_path, 't10k-images-idx3-ubyte.gz'),
        y_test_path=os.path.join(DATA_Base_path, 't10k-labels-idx1-ubyte.gz'),
        normalize=True,
        one_hot=False
    )
    return X_train, y_train, X_test, y_test


# 加载数据
X_train, y_train, X_test, y_test = load_mnist_data()

# 构建逻辑回归分类器：
# penalty="l1"  -> 使用 L1 正则，倾向产生稀疏权重；
# solver="saga" -> 支持 L1 且适合大规模数据；
# tol=0.1       -> 收敛容差（值越小通常越精细但训练更慢）。
clf = LogisticRegression(penalty="l1", solver="saga", tol=0.1)

# 在训练集上拟合模型参数。
clf.fit(X_train, y_train)

# 在测试集上评估准确率。
score = clf.score(X_test, y_test)
print("Test score with L1 penalty: %.4f" % score)

# 预测测试集标签，用于后续可视化分析。
y_pred = clf.predict(X_test)


# 可视化函数1：展示若干测试样本及模型预测结果。
# 作用：直观看到“输入图像-预测类别-真实类别”的对应关系，快速判断模型是否学到了有效特征。
def plot_prediction_samples(X, y_true, y_pred, num_samples=12):
    # MNIST 每张图像是 28x28，当前 X 的每一行是长度 784 的扁平向量。
    # 这里将其 reshape 回二维图像，便于显示。
    image_h, image_w = 28, 28

    # 选取前 num_samples 个样本进行展示（可根据需要改为随机采样）。
    num_samples = min(num_samples, X.shape[0])

    # 网格布局：固定 4 列，行数按样本数自动计算。
    n_cols = 4
    n_rows = int(np.ceil(num_samples / n_cols))

    plt.figure(figsize=(12, 3 * n_rows))
    for i in range(num_samples):
        plt.subplot(n_rows, n_cols, i + 1)

        # 将一维向量恢复为 28x28 灰度图。
        img = X[i].reshape(image_h, image_w)
        plt.imshow(img, cmap="gray")

        # 标题中同时显示预测值与真实值，便于对照。
        # 预测正确用绿色，预测错误用红色，一眼识别问题样本。
        is_correct = y_pred[i] == y_true[i]
        title_color = "green" if is_correct else "red"
        plt.title(f"Pred: {y_pred[i]} | True: {y_true[i]}", color=title_color, fontsize=10)

        # 关闭坐标轴，让图像更清晰。
        plt.axis("off")

    plt.suptitle("MNIST Test Samples: Prediction vs Ground Truth", fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


# 可视化函数2：绘制混淆矩阵。
# 作用：查看各数字类别之间的混淆情况，比如“4 常被误分为 9”这类细节。
def plot_confusion_matrix(y_true, y_pred):
    # labels 明确指定类别顺序，确保矩阵行列与 0-9 一一对应。
    labels = np.arange(10)
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    # ConfusionMatrixDisplay 直接提供标准可视化接口。
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    fig, ax = plt.subplots(figsize=(8, 8))
    disp.plot(ax=ax, cmap="Blues", xticks_rotation=45, colorbar=True)
    plt.title("MNIST Confusion Matrix (Logistic Regression)")
    plt.tight_layout()
    plt.show()


# 执行可视化：
# 1) 样本级别观察预测效果；
# 2) 全局类别级别观察错误分布。
plot_prediction_samples(X_test, y_test, y_pred, num_samples=12)
plot_confusion_matrix(y_test, y_pred)


'''

### package
numpy
matplotlib
sklearn
os
importlib

### 关键函数

```
resolve_mnist_raw_dir()
自动定位 MNIST 原始数据目录，按候选路径依次检查关键文件是否完整，返回可用目录。

os.path.join(...)
跨平台拼接文件路径，避免手动字符串拼接导致路径分隔符问题。

all(os.path.exists(...))
验证一个目录是否包含全部必须文件，用于判断该目录是否可直接用于训练。

importlib.util.spec_from_file_location(name, path)
为“文件路径导入”创建模块规格，不依赖 package 结构和 PYTHONPATH。

importlib.util.module_from_spec(spec)
基于模块规格创建模块对象。

spec.loader.exec_module(module)
执行模块代码，将模块中的函数/变量加载到 module 对象中。

load_mnist_data()
统一完成：定位数据目录、动态导入 load_data.py、读取训练集和测试集。

load_local_mnist(...)
从本地 gzip 文件读取 MNIST，并按参数决定是否归一化与 one-hot 编码。

LogisticRegression(penalty="l1", solver="saga", tol=0.1)
创建逻辑回归分类器，使用 L1 正则和 saga 求解器。

clf.fit(X_train, y_train)
根据训练数据学习模型参数。

clf.score(X_test, y_test)
返回模型在测试集上的平均准确率。

plot_prediction_samples(X, y_true, y_pred, num_samples=12)
可视化测试样本图像，展示每个样本的预测标签与真实标签，并用颜色区分是否预测正确。

confusion_matrix(y_true, y_pred, labels=np.arange(10))
生成 10 类分类任务的混淆矩阵，统计每个真实类别被预测到各类别的数量。

ConfusionMatrixDisplay(...).plot(...)
将混淆矩阵渲染为图像，便于观察类别间误判模式。

plot_confusion_matrix(y_true, y_pred)
封装混淆矩阵计算与绘图流程，快速查看模型在全类别上的错误分布。
```


'''