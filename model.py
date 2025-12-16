import gurobipy as gp
from gurobipy import GRB
from data import I, J, K, s_i, d_j, r_j, c_ij_k, t_ij_k, tilde_c_ji_k, tilde_t_ji_k, Q_k, T_max_k, lambda_weight

model = gp.Model("TP_with_Returns")

x = model.addVars(I, J, K, lb=0, vtype=GRB.CONTINUOUS, name="x")
y = model.addVars(J, I, K, lb=0, vtype=GRB.CONTINUOUS, name="y")
z = model.addVars(I, J, K, vtype=GRB.BINARY, name="z")
w = model.addVars(I, K, vtype=GRB.BINARY, name="w")  


model.setObjective(
    gp.quicksum(
        lambda_weight * c_ij_k[i,j,k] * x[i, j, k] +
        (1 - lambda_weight) * t_ij_k[i,j,k] * z[i, j, k] +
        lambda_weight * tilde_c_ji_k[j,i,k] * y[j, i, k] +
        (1 - lambda_weight) * tilde_t_ji_k[j,i,k] * z[i, j, k]
        for i in I for j in J for k in K
    ),
    GRB.MINIMIZE
)

# 1
for i in I:
    model.addConstr(gp.quicksum(x[i,j,k] for j in J for k in K) <= s_i[i])

# 2. 
for j in J:
    model.addConstr(gp.quicksum(x[i, j, k] for i in I for k in K) == d_j[j])

# 3. 
for i in I:
    for j in J:
        for k in K:
            model.addConstr(y[j,i,k] <= r_j[j] * z[i,j,k])

# 4. 
for j in J:
    model.addConstr(gp.quicksum(y[j, i, k] for i in I for k in K) == r_j[j])
                    
# 5. 
for i in I:
    for k in K:
        model.addConstr(gp.quicksum(x[i, j, k] for j in J) <= Q_k[k] * w[i,k]) 
        model.addConstr(gp.quicksum(y[j, i, k] for j in J) <= Q_k[k] * w[i,k]) 

# 8.
for k in K:
    model.addConstr(gp.quicksum((t_ij_k[(i, j, k)] + tilde_t_ji_k[(j, i, k)]) * z[i, j, k] for i in I for j in J) <= T_max_k[k])

# 6.
for k in K:
    model.addConstr(gp.quicksum(w[i,k] for i in I) == 1)

# 7.
for i in I:
    for j in J:
        for k in K:
            model.addConstr(z[i,j,k] <= w[i,k])



model.setParam('TimeLimit', 3600)
model.setParam('MIPGap', 0.01)
model.setParam('OutputFlag', 1)

model.optimize()

print("GIẢI PHÁP TỐI ƯU")
print("=" * 60)

if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
    print(f"Giá trị hàm mục tiêu: {model.ObjVal:.2f}")
    
    print("\nPHÂN PHỐI HÀNG TỪ KHO ĐẾN CỬA HÀNG")
    for k in K:
        for i in I:
            for j in J:
                if x[i, j, k].X > 1e-6:
                    print(
                        f"Chuyến {k}: Kho {i} → Cửa hàng {j} | "
                        f"Giao: {x[i, j, k].X:.2f}"
                    )

    print("\nHÀNG TRẢ VỀ")
    has_return = False
    for j in J:
        if r_j[j] > 0:
            printed_header = False
            for k in K:
                for i in I:
                    if y[j, i, k].X > 1e-6:
                        if not printed_header:
                            print(f"Cửa hàng {j} (tổng trả: {r_j[j]}):")
                            printed_header = True
                        print(
                            f"  → Kho {i} | Chuyến {k} | "
                            f"Trả: {y[j, i, k].X:.2f}"
                        )
                        has_return = True
    if not has_return:
        print("Không có hàng trả về")
    
    print("\nSỐ CHUYẾN XE")
    for k in K:
        for i in I:
            for j in J:
                if z[i, j, k].X > 0.5:
                    print(
                        f"Chuyến {k}: Kho {i} → Cửa hàng {j} | "
                        f"Giao: {x[i,j,k].X:.2f}, "
                        f"Trả: {y[j,i,k].X:.2f}"
                    )

elif model.status == GRB.INFEASIBLE:
    print("BÀI TOÁN KHÔNG KHẢ THI")
    print("Đang tính IIS...")
    model.computeIIS()
    print("\nCác ràng buộc gây xung đột:")
    for constr in model.getConstrs():
        if constr.IISConstr:
            print(f"Constraint: {constr.ConstrName}")
    print("\n=== CONFLICTING VARIABLE BOUNDS ===")
    for var in model.getVars():
        if var.IISLB:
            print(f"Variable {var.VarName} has conflicting LOWER bound")
        if var.IISUB:
            print(f"Variable {var.VarName} has conflicting UPPER bound")
    model.write("model_conflict.ilp")
    print("IIS written to model_conflict.ilp")

    
elif model.status == GRB.UNBOUNDED:
    print("Bài toán không bị chặn")
    
else:
    print(f"Tối ưu hóa không thành công. Mã trạng thái: {model.status}")


