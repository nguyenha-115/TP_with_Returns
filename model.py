from gurobipy import Model, GRB, quicksum
from data import I, J, K, s_i, d_j, r_j, c_ij_k, t_ij_k, tilde_c_ji_k, tilde_t_ji_k, Q_k, T_max_k, N_max_k, lambda_weight

m = Model("TP_with_Returns")

x = m.addVars(I, J, K, lb=0, vtype=GRB.CONTINUOUS, name="x")
y = m.addVars(J, I, K, lb=0, vtype=GRB.CONTINUOUS, name="y")
z = m.addVars(I, J, K, vtype=GRB.BINARY, name="z")
w = m.addVars(J, I, K, vtype=GRB.BINARY, name="w")

m.setObjective(
    quicksum(
        lambda_weight * c_ij_k[i,j,k] * x[i, j, k] +
        (1 - lambda_weight) * t_ij_k[i,j,k] * z[i, j, k] +
        lambda_weight * tilde_c_ji_k[j,i,k] * y[j, i, k] +
        (1 - lambda_weight) * tilde_t_ji_k[j,i,k] * w[j, i, k]
        for i in I for j in J for k in K
    ),
    GRB.MINIMIZE
)

# 1
for j in J:
    m.addConstr(quicksum(x[i, j, k] for i in I for k in K) == d_j[j])

# 2. 
for j in J:
    if r_j[j] > 0:  
        m.addConstr(quicksum(y[j, i, k] for i in I for k in K) == r_j[j])
    else:  
        for i in I:
            for k in K:
                m.addConstr(y[j, i, k] == 0)

# 3. 
for i in I:
    for j in J:
        for k in K:
            m.addConstr(y[j, i, k] <= Q_k[k] * w[j, i, k])

# 4. 
for i in I:
    m.addConstr(quicksum(x[i, j, k] for j in J for k in K) <= s_i[i])

# 5. 
for i in I:
    for j in J:
        for k in K:
            m.addConstr(x[i, j, k] <= Q_k[k] * z[i, j, k])

# 6.
for i in I:
    for j in J:
        m.addConstr(quicksum(z[i, j, k] for k in K) <= N_max_k[i,j])

# 7.
for i in I:
    for j in J:
        for k in K:
            m.addConstr(t_ij_k[i,j,k] * z[i, j, k] + tilde_t_ji_k[j,i,k] * w[j, i, k] <= T_max_k[k])

# 8.
# for i in I:
#     for j in J:
#         for k in K:
#             m.addConstr(w[j, i, k] <= z[i, j, k])

m.setParam('TimeLimit', 3600)
m.setParam('MIPGap', 0.01)
m.setParam('OutputFlag', 1)

m.optimize()

print("GIẢI PHÁP TỐI ƯU")
print("=" * 60)

if m.status == GRB.OPTIMAL:
    print(f"Giá trị hàm mục tiêu: {m.objVal:.2f}")
    
    print("\nPHÂN PHỐI HÀNG TỪ KHO ĐẾN CỬA HÀNG")
    for i in I:
        for j in J:
            for k in K:
                if x[i, j, k].X > 1e-6:
                    print(f"Kho {i} → Cửa hàng {j} bằng xe {k}: {x[i,j,k].X:.2f} đơn vị")
    
    print("\nHÀNG TRẢ VỀ")
    has_return = False
    for j in J:
        if r_j[j] > 0:
            print(f"\nCửa hàng {j} (tổng trả về: {r_j[j]} đơn vị):")
            for i in I:
                for k in K:
                    if y[j, i, k].X > 1e-6:
                        print(f"  → Kho {i} bằng xe {k}: {y[j,i,k].X:.2f} đơn vị")
                        has_return = True
    if not has_return:
        print("Không có hàng trả về")
    
    print("\nSỐ CHUYẾN XE")
    for i in I:
        for j in J:
            for k in K:
                if z[i,j,k].X > 0.5:
                    delivery = x[i,j,k].X
                    return_amt = y[j,i,k].X
                    print(f"Xe {k}: Kho {i} → Cửa hàng {j} (giao: {delivery:.2f}, trả: {return_amt:.2f})")
    
elif m.status == GRB.INFEASIBLE:
    print("Bài toán KHÔNG KHẢ THI")
    print("Tính toán IIS")
    m.computeIIS()
    print("\nCác ràng buộc xung đột:")
    for c in m.getConstrs():
        if c.IISConstr:
            print(f"  - {c.constrName}")
    
elif m.status == GRB.UNBOUNDED:
    print("Bài toán KHÔNG BỊ CHẶN")
    
else:
    print(f"Tối ưu hóa không thành công. Mã trạng thái: {m.status}")