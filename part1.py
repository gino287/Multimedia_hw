import numpy as np
import matplotlib.pyplot as plt
import math
# ======================================================================
# 共用函示
# ======================================================================
#計算點p到線段ab的最短距離
def dist_point_segment(p, a, b):
    """點 p 到線段 ab 的最短距離"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx*dx + dy*dy

    if L2 == 0:
        return math.hypot(p[0] - a[0], p[1] - a[1])

    t = ((p[0] - a[0]) * dx +
         (p[1] - a[1]) * dy) / L2

    # 1. 把 t 限制在 [0, 1]
    t = max(0, min(1, t))
    # 2. 計算線段上的最近點
    q = ( a[0] + (t*(b[0]-a[0])) , a[1] + (t*(b[1]-a[1]) ))
    # 3. 回傳 p 到最近點的距離
    p_q = math.hypot(p[0]-q[0], p[1]-q[1])
    return p_q

# ======================================================================
# 繪圖輔助：疊圖（提供 A 曲線點陣列與 B 折線點陣列）
# ======================================================================
def plot_overlay(P, curve_A, poly_B, title=""):
    """P: 控制點 (4,2)；curve_A: 公式法點列 (n,2)；poly_B: 中點法折線頂點 (m,2)"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(P[:, 0], P[:, 1], "k--o", lw=1, ms=5, label="control polygon")
    ax.plot(curve_A[:, 0], curve_A[:, 1], "b-", lw=2, label="A: formula")
    ax.plot(poly_B[:, 0], poly_B[:, 1], "r-o", lw=1.5, ms=4, label="B: mid-point")
    ax.set_aspect("equal")
    ax.legend()
    ax.set_title(title)
    return fig


# ======================================================================
# 公式法
# ======================================================================
def bezier_point(P, t):
    """
    P: [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]
    0 <= t <= 1
    回傳 (x, y)
    """
    #計算權重
    u = 1 - t
    w = [u**3, 3*t*u**2, 3*t**2*u, t**3]

    # 利用四個權重及控制點，
    # 分別計算 x、y，並回傳座標
    x=0.0
    y=0.0
    for i in range(4):
        x += w[i]*P[i][0]
        y += w[i]*P[i][1]
    
    return (x,y)
#等間距的產生n個點 陣列
def generate_curve(P, n):
    curve_A = []

    for t in np.linspace(0, 1, n):
        point = bezier_point(P, t)
        curve_A.append(point)

    return np.array(curve_A)
# ======================================================================
# 產生中點法折線
# ======================================================================

#找兩點中點
def mid(a, b):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
#切分 回傳左(右)半邊四個控制點
def split(P):
    """回傳 (L, R)：兩段子曲線各自的 4 個控制點"""
    b0, b1, b2, b3 = P
    m01, m12, m23 = mid(b0, b1), mid(b1, b2), mid(b2, b3)   # 第 1 層
    m012, m123 = mid(m01, m12), mid(m12, m23) #第 2 層
    M = mid(m012,m123) #第 3 層 M
    L =[b0,m01,m012,M]
    R=[M,m123,m23,b3]
    return (L,R)

#遞迴找出深度為depth的控制點，會回傳點陣列
def subdivide(P, depth):
    """回傳折線的點列表，共 2**depth + 1 個點"""
    if depth == 0:
        return [P[0], P[3]]
    else:
        L, R = split(P)
        left = subdivide(L,depth-1)
        right = subdivide(R,depth-1)
        return left +right[1:]
    


# ======================================================================
# Part 1.1 兩種方法疊圖 主流程
# ======================================================================
# 使用 100 × 100 的邏輯像素座標範圍
# 1 座標單位 = 1 pixel
W, H = 100, 100
P = np.array([
    [0, 0],       # P0：起點
    [20, 50],     # P1：第一控制點
    [80, 50],     # P2：第二控制點
    [100, 0]      # P3：終點
], dtype=float)

def part1_1():
    # 產生公式法座標陣列
    curve_A = generate_curve(P, 15)
    # 產生中點法折線
    poly_B = np.array(subdivide(P, 2))
    

    fig = plot_overlay(P, curve_A, poly_B, "depth = 2")
    fig.savefig("part1_overlay.png", dpi=300)
    plt.show()
    
# ==========================
# Part 1.2：誤差與收斂分析 主流程   
# ==========================
def part1_2():
    
    #先找尋適當的公式曲線座標數量
    max_sample_gap = float('-inf')
    #當數量為2000的時候每相鄰座標距離小於0.1
    curve_A = generate_curve(P,2000)
    for i in range(len(curve_A)-1):
        d = curve_A[i+1]-curve_A[i]
        distance = math.hypot(*d)
        
        max_sample_gap = max(max_sample_gap, distance)
    print("最大的間隔距離為:",max_sample_gap)
    
    #找出不同depth時的誤差
    depth = 0
    depths = []
    errors = []
    while 1:
        #找出兩條線之間的最大誤差
        max_distance =  float('-inf')
        poly_B = np.array(subdivide(P, depth))

        for i in range (len(curve_A)):
            #拿公式曲線的某一點對所有的線段距離，找出到折線的最短距離
            min_distance =  float('inf')
            for j in range(len(poly_B)-1):
                distance = dist_point_segment(curve_A[i],poly_B[j],poly_B[j+1])
                min_distance = min(min_distance,distance)
            
            #針對公式曲線每一點到中點法的最短距離，找出其中最大的
            max_distance = max(max_distance,min_distance)
            
        print("中點法depth:",depth ,"兩曲線的最大誤差為:",max_distance)
        depths.append(depth)
        errors.append(max_distance)
        if max_distance < 0.5:
            break
        depth+=1
    
    print(depths)
    print(errors)
    
    # 將實驗結果存成 CSV，方便後續製作報告
    data = np.column_stack((depths, errors))

    np.savetxt(
        "part1_2_errors.csv",
        data,
        delimiter=",",
        header="depth,max_error_px",
        comments="",
        fmt=["%d", "%.10f"]
    )
            
        
        
# ==========================
# Part 1.3：三段 Bézier 曲線 主流程 
# ========================== 
def part1_3():
    P1 = np.array([
        [0, 0],
        [20, 50],
        [80, 50],
        [100, 0]
    ], dtype=float)

    P2 = np.array([
        [100, 0],
        [120, -50],
        [160, -80],
        [200, 0]
    ], dtype=float)

    P3 = np.array([
        [200, 0],
        [240, 0],
        [260, 60],
        [300, 100]
    ], dtype=float)
    
    curve_A = generate_curve(P1, 2000)
    curve_B = generate_curve(P2, 2000)
    curve_C = generate_curve(P3, 2000)
    
    #畫線
    fig, ax = plt.subplots(figsize=(8, 6))

    # 畫三段曲線
    ax.plot(curve_A[:, 0], curve_A[:, 1], "b-", label="segment 1")
    ax.plot(curve_B[:, 0], curve_B[:, 1], "g-", label="segment 2")
    ax.plot(curve_C[:, 0], curve_C[:, 1], "r-", label="segment 3")

    # 畫三段控制多邊形
    ax.plot(P1[:, 0], P1[:, 1], "b--o", alpha=0.6)
    ax.plot(P2[:, 0], P2[:, 1], "g--o", alpha=0.6)
    ax.plot(P3[:, 0], P3[:, 1], "r--o", alpha=0.6)

    ax.set_aspect("equal")
    ax.legend()
    ax.set_title("Part 1.3: three Bezier segments")
    fig.savefig("part1_3_joins.png", dpi=300)
    plt.show()
    
    
    #更改控制點達到等長與不等長得比較
    P2_unequal = P2.copy()
    P2_unequal[1] = [110, -25]
    curve_B_unequal = generate_curve(P2_unequal, 2000)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # 左圖：等長
    axes[0].plot(curve_A[:,0], curve_A[:,1], "b-")
    axes[0].plot(curve_B[:,0], curve_B[:,1], "g-")
    axes[0].plot(P1[:,0], P1[:,1], "b--o", alpha=0.5)
    axes[0].plot(P2[:,0], P2[:,1], "g--o", alpha=0.5)
    axes[0].set_title("Equal-length")

    # 右圖：不等長
    axes[1].plot(curve_A[:,0], curve_A[:,1], "b-")
    axes[1].plot(curve_B_unequal[:,0], curve_B_unequal[:,1], "g-")
    axes[1].plot(P1[:,0], P1[:,1], "b--o", alpha=0.5)
    axes[1].plot(P2_unequal[:,0], P2_unequal[:,1], "g--o", alpha=0.5)
    axes[1].set_title("Unequal-length")

    for ax in axes:
        ax.set_aspect("equal")
        ax.set_xlim(-10, 210)
        ax.set_ylim(-90, 60)
        ax.grid(alpha=0.2)

    fig.tight_layout()
    fig.savefig("part1_3_length_comparison.png", dpi=300)
    plt.show()

# ==========================
# 統一執行入口
# ==========================
def main():
    # part1_1()
    # part1_2()
    part1_3()
        
if __name__ == "__main__":
    main()
