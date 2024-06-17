import os
from sklearn.cluster import KMeans
import numpy as np
# 定义各个小区的坐标
os.environ["OMP_NUM_THREADS"] = '1'
coordinates = np.array([
    [4, 8], # A1
    [6, 5], # A2
    [3, 7], # A3
    [8, 5], # A4
    [1, 2], # A5
    [6, 6]  # A6
])

# 使用KMeans进行聚类，k设为2（寻找两个聚类中心）
kmeans = KMeans(n_clusters=2, init='random', n_init=10, max_iter=300, random_state=0)
kmeans.fit(coordinates)

# 获取聚类中心（即安全岗亭的最优建设位置）
cluster_centers = kmeans.cluster_centers_
print(cluster_centers)
