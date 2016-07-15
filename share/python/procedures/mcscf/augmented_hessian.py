import numpy as np
import psi4
import os

# Relative hack for now
import sys, inspect
path_dir = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../../")))
sys.path.append(path_dir)
import p4util
from p4util.exceptions import *
np.set_printoptions(precision=5, linewidth=200, threshold=2000, suppress=True)

def ah_iteration(mcscf_obj, tol=5e-3, max_iter=15, lindep=1e-14, print_micro=True):
    """
    Solve the generalized eigenvalue problem:
    | 0,  g.T | | 1/l | =   | 1/l |
    | g,  H/l | | X   | = e | X   |

    Where g is the gradient, H is the orbital Hessian, X is our orbital update step, 
    and l is the eigenvalue.

    In some ways this is the subspace reduction of the full MCSCF Hessian where the
    CC part has been solved exactly. When this occurs the OC and CO elements collapse
    to the above and the CC Hessian becomes diagonally dominant.
   
    We can solve this through Davidson iterations where we condition the edges. It's the 
    Pulay equations all over again, just iterative.

    Watch out for lambdas that are zero. Looking for the lambda that is ~1.
 
    """

    # Unpack information
    orb_grad = mcscf_obj.gradient()
    precon = mcscf_obj.H_approx_diag()
    approx_step = mcscf_obj.approx_solve()
    orb_grad_ssq = orb_grad.sum_of_squares()

    # Gears
    min_lambda = 0.3
    converged = False

    fullG = np.zeros((max_iter + 2, max_iter + 2))
    fullS = np.zeros((max_iter + 2, max_iter + 2))
    fullS[np.diag_indices_from(fullS)] = 1

    guesses = []
    sigma_list = []
    guesses.append(approx_step)
    sigma_list.append(mcscf_obj.compute_Hk(approx_step))

    if print_micro:
        psi4.print_out("\n                             Eigenvalue          Rel dE          dX \n")

    # Run Davidson look for lambda ~ 1
    old_val = 0
    for microi in range(1, max_iter + 1):

        # Gradient
        fullG[0,microi] = guesses[-1].vector_dot(orb_grad)
        for i in range(microi):
            fullG[i + 1, microi] = guesses[-1].vector_dot(sigma_list[i])
            fullS[i + 1, microi] = guesses[-1].vector_dot(guesses[i])

        fullG[microi] = fullG[:, microi]
        fullS[microi] = fullS[:, microi]

        wlast = old_val

        # Slice out relevant S and G
        S = fullS[:microi + 1, :microi + 1]
        G = fullG[:microi + 1, :microi + 1]

        # Diagonalize the subspace
        # svals, vecs = np.linalg.eigh(S)

        # Solve Gv = lSv
        # S = LL.T
        # L^-1 A L^-1T LT v = l L^-1T v
        L = np.linalg.cholesky(S)

        # So unstable man, who thought it was a good idea to invert
        # and divide by small numbers. Davidson, thats who.
        Ldiag = np.diag(L).copy() ** -0.5
        tL = L * Ldiag[:, None] * Ldiag
        eigvals, eigvecs = np.linalg.eigh(tL)

        # Check the range
        maxval = np.max(np.abs(eigvals[[0, -1]])) * 1.e-12

        # Zero out the ones outside the interval
        eigvals[(np.abs(eigvals) < maxval)] = 0
        eigvals[np.abs(eigvals) > 1.e-16] = eigvals[np.abs(eigvals) > 1.e-16] ** -1
        invL = np.dot(eigvecs * eigvals, eigvecs.T)
        invL *= Ldiag * Ldiag[:, None]

        # Solve in S basis, rotate back
        evals, evecs = np.linalg.eigh(np.dot(invL, G).dot(invL.T))
        vectors = np.dot(invL.T, evecs)

        # Figure out the right root to follow
        if np.sum(np.abs(vectors[0]) > min_lambda) == 0:
            raise PsiException("Augmented Hessian: Could not find the correct root!\n"\
                               "Try starting AH when the MCSCF wavefunction is more converged.")

        if np.sum(np.abs(vectors[0]) > min_lambda) > 1:
            psi4.print_out("   Warning! Multiple eigenvectors found to follow. Following closest to \lambda = 1.\n")

        idx = (np.abs(1 - np.abs(vectors[0]))).argmin()
        lam = abs(vectors[0, idx])
        subspace_vec = vectors[1:, idx]

        # Negative roots should go away?
        if idx > 0 and evals[idx] < -5.0e-6:
            psi4.print_out('   Warning! AH might follow negative eigenvalues!\n')

        diff_val = evals[idx] - old_val
        old_val = evals[idx]

        new_guess = guesses[0].clone()
        new_guess.zero()
        for num, c in enumerate(subspace_vec / lam):
            new_guess.axpy(c, guesses[num])

        # Build estimated sigma vector
        new_dx = sigma_list[0].clone()
        new_dx.zero()
        for num, c in enumerate(subspace_vec):
            new_dx.axpy(c, sigma_list[num])

        # Consider restraints
        new_dx.axpy(lam, orb_grad)
        new_dx.axpy(old_val * lam, new_guess)

        norm_dx = (new_dx.sum_of_squares() / orb_grad_ssq) ** 0.5

        if print_micro:
            psi4.print_out("      AH microiter %2d   % 18.12e   % 6.4e   % 6.4e\n" % (microi, evals[idx],
                                    diff_val / evals[idx], norm_dx))

        if abs(old_val - wlast) < tol and norm_dx < (tol ** 0.5):
            converged = True
            break

        # Apply preconditioner
        tmp = precon.clone()
        val = tmp.clone()
        val.set(evals[idx])
        tmp.subtract(val)
        new_dx.apply_denominator(tmp)

        guesses.append(new_dx)
        sigma_list.append(mcscf_obj.compute_Hk(new_dx))

    if print_micro and converged:
        psi4.print_out("\n")
        #    psi4.print_out("      AH converged!       \n\n")

    #if not converged:
    #    psi4.print_out("      !Warning. Augmented Hessian did not converge.\n")

    new_guess.scale(-1.0)

    return converged, microi, new_guess

