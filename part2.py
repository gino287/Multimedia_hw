import numpy as np
import matplotlib.pyplot as plt
import math


# ======================================================================
# 共用函示
# ======================================================================

def edge_crossing(p0, p1, y):
    """邊 p0→p1 和水平線 y 的交點。回傳 (x, dir) 或 None"""
    
    (x0, y0), (x1, y1) = p0, p1
    
    #如果兩個點都在水平線的同一側代表沒有相交
    if (y0 <= y) == (y1 <= y):      
        return None
    
    else:    
        x = x0 +( y-y0 ) * (x1 - x0) / (y1-y0)
        d = 1 if y1 > y0 else -1         # 由y座標增加的方向穿過水平線 = +1 否則-1
        return (x, d)
    
def fill_nonzero(paths, W, H):
    """paths: [[(x,y), ...], ...] 每個子路徑自動封閉。回傳 img[y][x] in {0, 1}"""
    
    #建立畫布
    img = np.full((H, W), 255, dtype=np.uint8)
    
    #建立每條線段、向量
    edges = []
    for sp in paths:
        for i in range(len(sp)):
            p0 = sp[i]
            p1 = sp[(i+1) % len (sp)]
            edges.append((p0,p1))
    
    #針對每個y去套用交點函示，找到每一條水平線上與各線段的x交點座標
    for j in range(H):
        y = j + 0.5
        hits = [h for h in (edge_crossing(a, b, y) for a, b in edges) if h]
        hits.sort()
        
        #w不為0的區段 到下一個交點座標要全部塗色
        w = 0
        for k in range(len(hits) - 1):
            w += hits[k][1]
            if w != 0:
                img[j, math.ceil(hits[k][0]-0.5):math.ceil(hits[k+1][0]-0.5)] = 0
    return img
# ======================================================================
# 基本宣告
# ======================================================================
def init():
    W, H = 500, 500

    # 建立白色畫布
    canvas = np.full((H, W), 255, dtype=np.uint8)

    y=250
    x=250
    # 之後你自己決定哪些像素要塗黑
    # canvas[y, x] = 0

    # 顯示畫布
    plt.imshow(canvas, cmap="gray", vmin=0, vmax=255)
    plt.axis("equal")
    plt.show()
    

def main():
    init()

        
if __name__ == "__main__":
    main()