
const MOZNEIntervalySprav = [6, 12, 24, 48, 96, 192, 384, 768, 1536, 3072, 6144, 12288, 24576, 49152, 123456789];

const TEPLOTY = [null, -40, -39.5, -39, -38.5, -38, -37.5, -37, -36.5, -36, -35.5, -35, -34.5, -34, -33.5, -33, 
-32.5, -32, -31.5, -31, -30.5, -30, -29.5, -29, -28.5, -28, -27.5, -27, -26.5, -26, -25.5, -25, -24.5, 
-24, -23.5, -23, -22.5, -22, -21.5, -21, -20.5, -20, -19.5, -19, -18.5, -18, -17.5, -17, -16.5, -16, 
-15.5, -15, -14.5, -14, -13.5, -13, -12.5, -12, -11.5, -11, -10.5, -10, -9.5, -9, -8.5, -8, -7.5, -7, 
-6.5, -6, -5.5, -5, -4.5, -4, -3.5, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 
4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 
15.5, 16, 16.5, 17, 17.5, 18, 18.5, 19, 19.5, 20, 20.5, 21, 21.5, 22, 22.5, 23, 23.5, 24, 24.5, 25, 
25.5, 26, 26.5, 27, 27.5, 28, 28.5, 29, 29.5, 30, 30.5, 31, 31.5, 32, 32.5, 33, 33.5, 34, 34.5, 35, 
35.5, 36, 36.5, 37, 37.5, 38, 38.5, 39, 39.5, 40, 40.5, 41, 41.5, 42, 42.5, 43, 43.5, 44, 44.5, 45, 
45.5, 46, 46.5, 47, 47.5, 48, 48.5, 49, 49.5, 50, 50.5, 51, 51.5, 52, 52.5, 53, 53.5, 54, 54.5, 55, 
55.5, 56, 56.5, 57, 57.5, 58, 58.5, 59, 59.5, 60, 60.5, 61, 61.5, 62, 62.5, 63, 63.5, 64, 64.5, 65, 
65.5, 66, 66.5, 67, 67.5, 68, 68.5, 69, 69.5, 70, 70.5, 71, 71.5, 72, 72.5, 73, 73.5, 74, 74.5, 75, 
75.5, 76, 76.5, 77, 77.5, 78, 78.5, 79, 79.5, 80]

const VLHKOSTI = [null, 0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 
4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.5, 15, 
15.5, 16, 16.5, 17, 17.5, 18, 18.5, 19, 19.5, 20, 20.5, 21, 21.5, 22, 22.5, 23, 23.5, 24, 24.5, 25, 
25.5, 26, 26.5, 27, 27.5, 28, 28.5, 29, 29.5, 30, 30.5, 31, 31.5, 32, 32.5, 33, 33.5, 34, 34.5, 35, 
35.5, 36, 36.5, 37, 37.5, 38, 38.5, 39, 39.5, 40, 40.5, 41, 41.5, 42, 42.5, 43, 43.5, 44, 44.5, 45, 
45.5, 46, 46.5, 47, 47.5, 48, 48.5, 49, 49.5, 50, 50.5, 51, 51.5, 52, 52.5, 53, 53.5, 54, 54.5, 55, 
55.5, 56, 56.5, 57, 57.5, 58, 58.5, 59, 59.5, 60, 60.5, 61, 61.5, 62, 62.5, 63, 63.5, 64, 64.5, 65, 
65.5, 66, 66.5, 67, 67.5, 68, 68.5, 69, 69.5, 70, 70.5, 71, 71.5, 72, 72.5, 73, 73.5, 74, 74.5, 75, 
75.5, 76, 76.5, 77, 77.5, 78, 78.5, 79, 79.5, 80, 80.5, 81, 81.5, 82, 82.5, 83, 83.5, 84, 84.5, 85, 
85.5, 86, 86.5, 87, 87.5, 88, 88.5, 89, 89.5, 90, 90.5, 91, 91.5, 92, 92.5, 93, 93.5, 94, 94.5, 95, 
95.5, 96, 96.5, 97, 97.5, 98, 98.5, 99, 99.5, 100]

const CODE = ['00', '10', '20', '30', '40', '50', '60', '70', '80', '90', '?0', '@0', 'A0', 'B0', 'C0', 'D0', 
'E0', 'F0', 'G0', 'H0', 'I0', 'J0', 'K0', 'L0', 'M0', 'N0', 'O0', 'P0', 'Q0', 'R0', 'S0', 'T0', 'U0', 'V0',
 'W0', 'X0', 'Y0', 'Z0', 'a0', 'b0', 'c0', 'd0', 'e0', 'f0', 'g0', 'h0', 'i0', 'j0', 'k0', 'l0', 'm0', 'n0', 
 'o0', 'p0', 'q0', 'r0', 's0', 't0', 'u0', 'v0', 'w0', 'x0', 'y0', 'z0', '01', '11', '21', '31', '41', '51', 
 '61', '71', '81', '91', '?1', '@1', 'A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1', 'I1', 'J1', 'K1', 'L1', 
 'M1', 'N1', 'O1', 'P1', 'Q1', 'R1', 'S1', 'T1', 'U1', 'V1', 'W1', 'X1', 'Y1', 'Z1', 'a1', 'b1', 'c1', 'd1', 
 'e1', 'f1', 'g1', 'h1', 'i1', 'j1', 'k1', 'l1', 'm1', 'n1', 'o1', 'p1', 'q1', 'r1', 's1', 't1', 'u1', 'v1', 
 'w1', 'x1', 'y1', 'z1', '02', '12', '22', '32', '42', '52', '62', '72', '82', '92', '?2', '@2', 'A2', 'B2',
  'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2', 'J2', 'K2', 'L2', 'M2', 'N2', 'O2', 'P2', 'Q2', 'R2', 'S2', 'T2', 
  'U2', 'V2', 'W2', 'X2', 'Y2', 'Z2', 'a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2', 'i2', 'j2', 'k2', 'l2', 
  'm2', 'n2', 'o2', 'p2', 'q2', 'r2', 's2', 't2', 'u2', 'v2', 'w2', 'x2', 'y2', 'z2', '03', '13', '23', '33', 
  '43', '53', '63', '73', '83', '93', '?3', '@3', 'A3', 'B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'I3', 'J3', 
  'K3', 'L3', 'M3', 'N3', 'O3', 'P3', 'Q3', 'R3', 'S3', 'T3', 'U3', 'V3', 'W3', 'X3', 'Y3', 'Z3', 'a3', 'b3', 
  'c3', 'd3', 'e3', 'f3', 'g3', 'h3', 'i3', 'j3', 'k3', 'l3', 'm3', 'n3', 'o3', 'p3', 'q3', 'r3', 's3', 't3', 
  'u3', 'v3', 'w3', 'x3', 'y3', 'z3'];

  module.exports = {
    MOZNEIntervalySprav: MOZNEIntervalySprav,
    TEPLOTY: TEPLOTY,
    VLHKOSTI: VLHKOSTI,
    CODE: CODE
  }