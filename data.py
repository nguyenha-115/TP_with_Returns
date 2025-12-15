import numpy as np
import random

np.random.seed(42)  

I = list(range(1, 6))
J = list(range(1, 11))
K = list(range(1, 5))

# giả sử tọa độ trong 100x100 km
coord_i = {i: (np.random.uniform(0,100), np.random.uniform(0,100)) for i in I}
coord_j = {j: (np.random.uniform(0,100), np.random.uniform(0,100)) for j in J}

def euclid_distance(p1, p2):
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

s_i = {i: int(np.random.uniform(100, 200)) for i in I}

d_j = {j: int(np.random.uniform(20, 50)) for j in J}

r_j = {j: int(d_j[j]*np.random.uniform(0.1,0.4)) for j in J}

c_ij_k = {}
t_ij_k = {}
tilde_c_ji_k = {}
tilde_t_ji_k = {}

for i in I:
    for j in J:
        dist = euclid_distance(coord_i[i], coord_j[j])
        for k in K:
            c_ij_k[(i,j,k)] = dist * np.random.uniform(0.9,1.1)
            t_ij_k[(i,j,k)] = dist * np.random.uniform(0.04,0.06)

            tilde_c_ji_k[(j,i,k)] = dist * np.random.uniform(0.8,1.0)
            tilde_t_ji_k[(j,i,k)] = dist * np.random.uniform(0.03,0.05)

Q_k = {k: int(np.random.uniform(60,120)) for k in K}

T_max_k = {k: float(np.random.uniform(8,12)) for k in K}

N_max_k = {}
for i in I:
    for j in J:
        dist = euclid_distance(coord_i[i], coord_j[j])
        if dist < 30:
            N_max_k[(i,j)] = np.random.randint(2,4)
        elif dist < 60:
            N_max_k[(i,j)] = np.random.randint(1,3)
        else:
            N_max_k[(i,j)] = 1

lambda_weight = 0.6


if __name__ == "__main__":
    print("I =", I)
    print("J =", J)
    print("K =", K)
    print("coord_i =", coord_i)
    print("coord_j =", coord_j)
    print("s_i =", s_i)
    print("d_j =", d_j)
    print("r_j =", r_j)
    print("c_ij_k =", c_ij_k)
    print("t_ij_k =", t_ij_k)
    print("tilde_c_ji_k =", tilde_c_ji_k)
    print("tilde_t_ji_k =", tilde_t_ji_k)
    print("Q_k =", Q_k)
    print("T_max_k =", T_max_k)
    print("N_max_k =", N_max_k)
    print("lambda_weight =", lambda_weight)
