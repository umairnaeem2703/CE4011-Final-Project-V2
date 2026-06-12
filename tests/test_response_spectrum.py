import math
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from results import ModalResults
from rsa_solver import ResponseSpectrumSolver, cqc, cqc_coefficient, interpolate_spectrum, srss


def _modal_results(eigenvalues, periods, mode_shapes, gammas):
    return ModalResults(
        K=[[4.0, 0.0], [0.0, 9.0]],
        M=[[1.0, 0.0], [0.0, 1.0]],
        eigenvalues=eigenvalues,
        frequencies=[1.0 / period for period in periods],
        periods=periods,
        mode_shapes=mode_shapes,
        modal_masses=[1.0 for _ in eigenvalues],
        participation_factors=gammas,
        effective_masses=[gamma * gamma for gamma in gammas],
        mass_participation_ratios=[0.5 for _ in eigenvalues],
        influence_vector=[1.0, 1.0],
        total_participating_mass=2.0,
        num_modes_requested=len(eigenvalues),
        num_modes_extracted=len(eigenvalues),
    )


def test_spectrum_interpolation_linear():
    """Verify: Sa(0.5) linearly interpolates halfway between 2 and 4."""
    assert abs(interpolate_spectrum(0.5, [0.0, 1.0], [2.0, 4.0]) - 3.0) < 1.0e-12


def test_single_mode_modal_response_vector():
    """Verify: u_n,max = phi_n * Gamma_n * Sa / omega_n^2."""
    modal = _modal_results([4.0], [0.5], [[2.0, 0.0]], [3.0])
    results = ResponseSpectrumSolver(modal, [0.5], [8.0]).solve()

    assert abs(results.modal_response_vectors[0][0] - 12.0) < 1.0e-12


def test_srss_combination():
    """Verify: SRSS combines modal scalar values by sqrt(sum R_n^2)."""
    assert abs(srss([3.0, 4.0]) - 5.0) < 1.0e-12


def test_cqc_coefficient_is_symmetric_and_bounded():
    """Verify: CQC rho_ij equals rho_ji and stays between zero and one."""
    rho_12 = cqc_coefficient(2.0, 3.0, 0.05)
    rho_21 = cqc_coefficient(3.0, 2.0, 0.05)

    assert abs(rho_12 - rho_21) < 1.0e-12 and 0.0 <= rho_12 <= 1.0


def test_cqc_combination():
    """Verify: widely separated modes with zero damping reduce to SRSS."""
    value, rho = cqc([3.0, 4.0], [2.0, 8.0], 0.0)

    assert abs(value - 5.0) < 1.0e-12 and rho[0][1] == 0.0
