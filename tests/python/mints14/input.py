#! Check for correctness of ESP values. The ESP values are calculated using one or four threads
#! The one thread values are checked against the four thread values. The one thread values are 
#! also checked against the reference values (1 thread values computed, when generating this test).
#! Caution: The reference values are not obtained using an actual physical reference, but rather
#! generated by Psi4 at one point in time.

import psi4
import psi4.core as p4c
import numpy as np

psi4.set_output_file("output.dat", False)

#H2O with minimal basis
h2o = psi4.geometry("""
O
H 1 0.96
H 1 0.96 2 104.5
""")


ene, wfn = psi4.energy('scf/STO-3G', return_wfn = True)
myepc = p4c.ESPPropCalc(wfn)

# Number of points to evaluate the ESP on per dimension (reference values below were generated with 5)
numpoints_per_dim = 5
points = np.array([ [float(x),float(y),float(z) ] for x in range(0,numpoints_per_dim) for y in range(0,numpoints_per_dim) for z in range(0,numpoints_per_dim) ])
psi4_matrix = p4c.Matrix.from_array(points)

# We calculate the ESPs with 1 thread
psi4.set_num_threads(1, quiet = True)
esps_1threads = np.array(myepc.compute_esp_over_grid_in_memory(psi4_matrix))
# We calculate the ESPs with 4 threads
psi4.set_num_threads(4, quiet = True)
esps_4threads = np.array(myepc.compute_esp_over_grid_in_memory(psi4_matrix))

# Reference values (Generated with psi4 master on 22.05.20 at 23:30 GMT
reference_esps = [ 4.62483342e+01,  1.54804313e-01,  4.13685593e-02,  1.99074762e-02,
                   1.15152678e-02,  2.05265305e-01,  2.83124071e-01,  3.85914212e-02,
                   1.81738886e-02,  1.07752887e-02,  1.77818258e-02,  3.68574105e-02,
                   2.25974306e-02,  1.35771735e-02,  8.87906889e-03,  5.10066439e-03,
                   1.12829223e-02,  1.12265555e-02,  8.83213803e-03,  6.63860586e-03,
                   2.19102261e-03,  4.93006854e-03,  5.89615996e-03,  5.53808484e-03,
                   4.71886332e-03, -5.17239329e-02,  3.13726711e-02,  2.75355388e-02,
                   1.65919492e-02,  1.03990059e-02, -3.35874097e-03,  4.15222788e-02,
                   2.56191309e-02,  1.52660739e-02,  9.76796362e-03,  6.32834557e-03,
                   2.04241605e-02,  1.70973880e-02,  1.17455466e-02,  8.13966708e-03,
                   3.38098123e-03,  8.74425646e-03,  9.48996966e-03,  7.93026739e-03,
                   6.17969093e-03,  1.74806282e-03,  4.26579485e-03,  5.29784951e-03,
                   5.12333890e-03,  4.45846711e-03, -1.57567665e-02,  5.30695677e-03,
                   1.23293022e-02,  1.06586884e-02,  7.93900611e-03, -7.73802957e-03,
                   7.26178250e-03,  1.17147293e-02,  9.98332008e-03,  7.52680394e-03,
                  -4.70874042e-04,  7.07678716e-03,  9.28214077e-03,  8.16156593e-03,
                   6.44348860e-03,  1.00781695e-03,  4.75096863e-03,  6.24946368e-03,
                   5.97476305e-03,  5.07885832e-03,  9.07850148e-04,  2.91174728e-03,
                   3.98405846e-03,  4.14293807e-03,  3.80513995e-03, -5.01856357e-03,
                   1.66005706e-03,  5.58988126e-03,  6.25608633e-03,  5.51718510e-03,
                  -3.54538877e-03,  2.13874136e-03,  5.42317564e-03,  5.96499476e-03,
                   5.28687977e-03, -1.26041313e-03,  2.57086533e-03,  4.76216983e-03,
                   5.15904477e-03,  4.66727597e-03, -6.98718627e-05,  2.29543121e-03,
                   3.72078488e-03,  4.09219098e-03,  3.84409282e-03,  2.86099206e-04,
                   1.74337099e-03,  2.70404545e-03,  3.07010847e-03,  3.01768294e-03,
                  -2.17493011e-03,  7.08011269e-04,  2.82422496e-03,  3.69989978e-03,
                   3.71459579e-03, -1.77325890e-03,  8.55302891e-04,  2.77277336e-03,
                   3.57535348e-03,  3.59320794e-03, -9.75050076e-04,  1.08091443e-03,
                   2.57027134e-03,  3.22234880e-03,  3.25925100e-03, -3.45599629e-04,
                   1.12615341e-03,  2.20372521e-03,  2.71976417e-03,  2.79365593e-03,
                  -1.83114358e-05,  1.00066735e-03,  1.76948007e-03,  2.18338059e-03,
                   2.29358229e-03]

# Comparison
psi4.compare_arrays(esps_1threads, esps_4threads, 3, "Reference value for ESP calculation, 1 thread vs. 4 threads.")
psi4.compare_arrays(esps_1threads, reference_esps, 3, "Reference value for ESP calculation, 1 thread vs. reference calculation.")

# We calculate the EF with 1 thread
psi4.set_num_threads(1, quiet = True)
efs_1threads = np.array(myepc.compute_field_over_grid_in_memory(psi4_matrix))

# # We calculate the EF with 4 threads
psi4.set_num_threads(4, quiet = True)
efs_4threads = np.array(myepc.compute_field_over_grid_in_memory(psi4_matrix))

# Reference fields (Generated with psi4 master (#6491598) on 13.11.20 at 11:52 GMT
reference_efs = [[ 0.00000000e+00,  0.00000000e+00,  4.77186106e+02],
                 [ 0.00000000e+00,  0.00000000e+00,  1.85623832e-01],
                 [ 0.00000000e+00,  1.73472348e-18,  1.91346393e-02],
                 [ 0.00000000e+00, -4.33680869e-19,  6.55588449e-03],
                 [ 0.00000000e+00,  0.00000000e+00,  2.94337286e-03],
                 [ 0.00000000e+00,  2.95691183e-01, -4.53422214e-01],
                 [ 0.00000000e+00,  2.67947363e-01,  5.28430344e-01],
                 [ 0.00000000e+00,  5.88889250e-03,  2.06451109e-02],
                 [ 0.00000000e+00,  1.83416201e-03,  5.76565566e-03],
                 [ 0.00000000e+00,  7.54931454e-04,  2.62530100e-03],
                 [ 0.00000000e+00,  1.57991091e-02, -2.11018928e-02],
                 [ 0.00000000e+00,  2.97891090e-02,  4.78297893e-03],
                 [ 0.00000000e+00,  8.19544559e-03,  6.59313520e-03],
                 [ 0.00000000e+00,  2.72831640e-03,  3.33703101e-03],
                 [ 0.00000000e+00,  1.17248482e-03,  1.82648818e-03],
                 [ 0.00000000e+00,  2.63620499e-03, -4.58659567e-03],
                 [ 0.00000000e+00,  5.68903904e-03, -1.46558068e-03],
                 [ 0.00000000e+00,  4.06356238e-03,  1.03138146e-03],
                 [ 0.00000000e+00,  2.15851886e-03,  1.29928750e-03],
                 [ 0.00000000e+00,  1.13722701e-03,  1.00348445e-03],
                 [ 0.00000000e+00,  8.56111214e-04, -1.76826317e-03],
                 [ 0.00000000e+00,  1.89271231e-03, -1.00584394e-03],
                 [ 0.00000000e+00,  1.87517999e-03, -7.48722431e-05],
                 [ 0.00000000e+00,  1.35718958e-03,  3.71323515e-04],
                 [ 0.00000000e+00,  8.80439345e-04,  4.58309050e-04],
                 [ 3.62842257e-02,  0.00000000e+00, -6.94384092e-02],
                 [ 3.65964119e-02,  3.46944695e-18, -1.12411484e-02],
                 [ 1.03445436e-02,  2.60208521e-18,  6.86980374e-03],
                 [ 3.01200075e-03, -4.33680869e-19,  4.39840077e-03],
                 [ 1.08487836e-03,  2.16840434e-19,  2.37286536e-03],
                 [ 2.53196892e-02, -2.05081091e-02, -3.97198780e-02],
                 [ 4.70813911e-02,  4.87804158e-03,  4.00145246e-03],
                 [ 9.50337213e-03,  2.97309011e-03,  7.44323205e-03],
                 [ 2.65343519e-03,  1.39203563e-03,  3.90025552e-03],
                 [ 9.81747702e-04,  6.44543615e-04,  2.12675890e-03],
                 [ 6.66940691e-03,  1.49156575e-03, -1.14121175e-02],
                 [ 1.05952191e-02,  9.68152537e-03, -1.51552260e-03],
                 [ 4.57290940e-03,  4.92077573e-03,  3.12249037e-03],
                 [ 1.71359999e-03,  2.12937405e-03,  2.36936068e-03],
                 [ 7.27224467e-04,  1.01413721e-03,  1.50402030e-03],
                 [ 1.43916550e-03,  1.22484990e-03, -3.70952095e-03],
                 [ 2.20744344e-03,  3.62949000e-03, -1.58410833e-03],
                 [ 1.60036384e-03,  3.02543471e-03,  4.95860948e-04],
                 [ 8.72049985e-04,  1.79270950e-03,  9.71173147e-04],
                 [ 4.57318634e-04,  1.00727630e-03,  8.44725774e-04],
                 [ 4.12509841e-04,  5.75638218e-04, -1.58612235e-03],
                 [ 6.30983535e-04,  1.47703640e-03, -9.70076022e-04],
                 [ 5.81033334e-04,  1.55982611e-03, -1.60394041e-04],
                 [ 4.11593266e-04,  1.18775444e-03,  2.75722777e-04],
                 [ 2.62840582e-04,  7.99546526e-04,  3.91856444e-04],
                 [-1.14301361e-02, -8.67361738e-19, -1.07695979e-02],
                 [ 3.90829290e-03, -1.73472348e-18, -8.15555991e-03],
                 [ 5.41800886e-03,  8.67361738e-19, -3.53529917e-04],
                 [ 2.88370296e-03, -2.16840434e-19,  1.47154333e-03],
                 [ 1.38387991e-03, -2.16840434e-19,  1.30169381e-03],
                 [-3.09697459e-03, -5.77455740e-03, -8.37127332e-03],
                 [ 5.48567593e-03, -1.04179033e-03, -5.50945276e-03],
                 [ 4.99210548e-03,  7.85719481e-04,  2.84551915e-05],
                 [ 2.59978410e-03,  7.04120264e-04,  1.33735914e-03],
                 [ 1.26977641e-03,  4.22543852e-04,  1.18038221e-03],
                 [ 1.28296385e-03, -1.85552875e-03, -4.63560239e-03],
                 [ 4.00144677e-03,  1.03212292e-03, -2.68942671e-03],
                 [ 3.28525736e-03,  1.63315151e-03,  5.08656449e-05],
                 [ 1.85667428e-03,  1.14529971e-03,  8.89608661e-04],
                 [ 9.82566297e-04,  6.86778982e-04,  8.66246209e-04],
                 [ 9.14578731e-04, -1.32347240e-04, -2.30540069e-03],
                 [ 1.76132839e-03,  1.18977393e-03, -1.44712776e-03],
                 [ 1.62020868e-03,  1.44967546e-03, -2.09218401e-04],
                 [ 1.08784878e-03,  1.10129163e-03,  3.89079389e-04],
                 [ 6.58531716e-04,  7.22796457e-04,  5.10314630e-04],
                 [ 4.16687373e-04,  1.38541131e-04, -1.19893646e-03],
                 [ 7.16762642e-04,  7.55837935e-04, -8.47539795e-04],
                 [ 7.36263154e-04,  9.52729540e-04, -2.94513663e-04],
                 [ 5.80055269e-04,  8.25403335e-04,  8.49291429e-05],
                 [ 4.03770325e-04,  6.11059009e-04,  2.42818930e-04],
                 [-2.54930851e-03, -4.33680869e-19, -3.42840091e-03],
                 [ 8.59387634e-04, -4.33680869e-19, -3.09722979e-03],
                 [ 2.18801514e-03, -2.16840434e-19, -1.06418868e-03],
                 [ 1.78320967e-03,  2.16840434e-19,  1.67941100e-04],
                 [ 1.13241378e-03,  1.08420217e-19,  5.16976512e-04],
                 [-1.40674646e-03, -1.28897672e-03, -3.00725008e-03],
                 [ 1.18602159e-03, -3.74223899e-04, -2.59196722e-03],
                 [ 2.07706986e-03,  2.02317894e-04, -8.89587691e-04],
                 [ 1.65035593e-03,  3.03698946e-04,  1.60146414e-04],
                 [ 1.05631319e-03,  2.37319327e-04,  4.74154723e-04],
                 [-5.13563163e-05, -9.54553630e-04, -2.13124767e-03],
                 [ 1.28366283e-03, -2.47144580e-05, -1.70595268e-03],
                 [ 1.63796773e-03,  4.85361378e-04, -6.16196031e-04],
                 [ 1.29367916e-03,  5.25212195e-04,  1.03863118e-04],
                 [ 8.59327260e-04,  4.01031500e-04,  3.59125641e-04],
                 [ 2.93944897e-04, -3.51934887e-04, -1.34870686e-03],
                 [ 8.90411452e-04,  2.64034693e-04, -1.05652614e-03],
                 [ 1.04656838e-03,  5.75305304e-04, -4.47404228e-04],
                 [ 8.70186444e-04,  5.74702439e-04,  1.00362330e-05],
                 [ 6.20294372e-04,  4.51547988e-04,  2.17294907e-04],
                 [ 2.37081931e-04, -7.24049767e-05, -8.31791663e-04],
                 [ 5.03400058e-04,  2.91236028e-04, -6.66530072e-04],
                 [ 5.93333149e-04,  4.83714963e-04, -3.42938122e-04],
                 [ 5.31104808e-04,  4.93654625e-04, -6.25231120e-05],
                 [ 4.11842208e-04,  4.12457848e-04,  9.85127268e-05],
                 [-8.42819831e-04, -1.08420217e-19, -1.49460411e-03],
                 [ 2.79295542e-04,  2.16840434e-19, -1.41942351e-03],
                 [ 9.38038156e-04,  0.00000000e+00, -7.81227007e-04],
                 [ 9.92258235e-04,  1.08420217e-19, -1.87317941e-04],
                 [ 7.81410855e-04,  1.08420217e-19,  1.27287507e-04],
                 [-5.97125829e-04, -3.79755298e-04, -1.37910616e-03],
                 [ 3.63061171e-04, -1.31021975e-04, -1.28521300e-03],
                 [ 9.08362134e-04,  6.07419159e-05, -7.10817802e-04],
                 [ 9.37847191e-04,  1.30354714e-04, -1.74719261e-04],
                 [ 7.39869491e-04,  1.25749968e-04,  1.16183350e-04],
                 [-1.82953325e-04, -4.09294959e-04, -1.10541241e-03],
                 [ 4.52362270e-04, -8.18711829e-05, -9.92315897e-04],
                 [ 7.89766516e-04,  1.55470402e-04, -5.61407932e-04],
                 [ 7.87393944e-04,  2.36094511e-04, -1.52733690e-04],
                 [ 6.29223855e-04,  2.20222896e-04,  8.47326157e-05],
                 [ 4.44809882e-05, -2.48424922e-04, -8.06800681e-04],
                 [ 4.07558302e-04,  3.06044162e-05, -7.05944729e-04],
                 [ 5.94617785e-04,  2.22564547e-04, -4.20269365e-04],
                 [ 5.89143701e-04,  2.84872327e-04, -1.38704841e-04],
                 [ 4.85732587e-04,  2.63559971e-04,  4.21765372e-05],
                 [ 9.79431484e-05, -1.09066464e-04, -5.63407299e-04],
                 [ 2.94543076e-04,  9.13557097e-05, -4.90653651e-04],
                 [ 3.99793079e-04,  2.27763976e-04, -3.13890974e-04],
                 [ 4.03799551e-04,  2.74855411e-04, -1.29722537e-04],
                 [ 3.48015799e-04,  2.59140058e-04,  2.65049640e-06],
                 ]

# Comparison
psi4.compare_arrays(efs_1threads, efs_4threads, 3, "Reference value for EF calculation, 1 thread vs. 4 threads.")
psi4.compare_arrays(efs_1threads, reference_efs, 3, "Reference value for EF calculation, 1 thread vs. reference calculation.")
