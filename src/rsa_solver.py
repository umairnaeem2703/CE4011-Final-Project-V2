# src/rsa_solver.py

import math
from results import ModalResults, RSAResults


class RSASolverError(Exception):
    """Custom exception raised for errors during response spectrum analysis."""
    pass


def validate_phase_4_complete(modal_results: ModalResults) -> None:
    """Verify modal results exist before RSA."""
    if modal_results is None:
        raise RSASolverError("Phase 4 incomplete: run modal analysis first.")
    if not getattr(modal_results, "periods", None):
        raise RSASolverError("No modal periods extracted.")


def interpolate_spectrum(period: float, spectrum_periods: list, spectrum_accelerations: list) -> float:
    """Return linearly interpolated Sa for a period, clamped at spectrum ends."""
    if len(spectrum_periods) != len(spectrum_accelerations):
        raise RSASolverError("Spectrum periods and accelerations must have the same length.")
    if len(spectrum_periods) == 0:
        raise RSASolverError("Response spectrum must contain at least one point.")

    pairs = sorted(zip(spectrum_periods, spectrum_accelerations), key=lambda item: item[0])
    if period <= pairs[0][0]:
        return float(pairs[0][1])
    if period >= pairs[-1][0]:
        return float(pairs[-1][1])

    for i in range(len(pairs) - 1):
        t0, sa0 = pairs[i]
        t1, sa1 = pairs[i + 1]
        if t0 <= period <= t1:
            if abs(t1 - t0) <= 1.0e-15:
                return float(sa1)
            ratio = (period - t0) / (t1 - t0)
            return float(sa0 + ratio * (sa1 - sa0))

    return float(pairs[-1][1])


def srss(values: list) -> float:
    """Square-root-sum-of-squares modal combination."""
    return math.sqrt(sum(value * value for value in values))


def cqc_coefficient(omega_i: float, omega_j: float, damping_ratio: float) -> float:
    """Chopra CQC modal coupling coefficient for equal damping."""
    if omega_i <= 0.0 or omega_j <= 0.0:
        return 0.0
    if abs(omega_i - omega_j) <= 1.0e-12:
        return 1.0

    zeta = max(0.0, min(float(damping_ratio), 0.999999))
    if zeta <= 0.0:
        return 0.0

    ratio = min(omega_i, omega_j) / max(omega_i, omega_j)
    numerator = 8.0 * zeta**2 * math.sqrt(1.0 - zeta**2) * (ratio + 4.0 * zeta**2 * ratio**3)
    denominator = (1.0 - ratio**2) ** 2 + 4.0 * zeta**2 * ratio**2 * (1.0 + ratio**2)
    if abs(denominator) <= 1.0e-15:
        return 1.0
    return max(0.0, min(numerator / denominator, 1.0))


def cqc(values: list, omegas: list, damping_ratio: float) -> tuple[float, list]:
    """Complete quadratic combination for a scalar response quantity."""
    rho = _rho_matrix(omegas, damping_ratio)
    total = 0.0
    for i in range(len(values)):
        for j in range(len(values)):
            total += rho[i][j] * values[i] * values[j]
    return math.sqrt(max(total, 0.0)), rho


class ResponseSpectrumSolver:
    """Generalized RSA solver operating only on modal matrices/vectors."""

    def __init__(self, modal_results: ModalResults, spectrum_periods: list, spectrum_accelerations: list):
        validate_phase_4_complete(modal_results)
        self.modal_results = modal_results
        self.spectrum_periods = list(spectrum_periods)
        self.spectrum_accelerations = list(spectrum_accelerations)

    def solve(self, combination_method: str = "SRSS", damping_ratio: float = 0.05) -> RSAResults:
        method = combination_method.upper()
        if method not in ("SRSS", "CQC"):
            raise RSASolverError("Combination method must be 'SRSS' or 'CQC'.")

        modal_vectors = []
        modal_base_shears = []
        modal_otms = []
        spectrum_values = []
        periods = []
        omegas = []

        for mode_index in range(self.modal_results.num_modes_extracted):
            period = self.modal_results.periods[mode_index]
            omega_sq = self.modal_results.eigenvalues[mode_index]
            if omega_sq <= 0.0:
                continue

            gamma = self.modal_results.participation_factors[mode_index]
            phi = self.modal_results.mode_shapes[mode_index]
            sa = interpolate_spectrum(period, self.spectrum_periods, self.spectrum_accelerations)
            q_max = gamma * sa / omega_sq
            u_max = [component * q_max for component in phi]
            force_vector = _mat_vec_mul(self.modal_results.K, u_max)

            periods.append(period)
            omegas.append(math.sqrt(omega_sq))
            spectrum_values.append(sa)
            modal_vectors.append({dof: value for dof, value in enumerate(u_max)})
            modal_base_shears.append(sum(force_vector))
            modal_otms.append(0.0)

        combined_response = {}
        dof_count = len(self.modal_results.K)
        rho_matrix = _rho_matrix(omegas, damping_ratio) if method == "CQC" else []
        for dof in range(dof_count):
            modal_values = [vector.get(dof, 0.0) for vector in modal_vectors]
            if method == "SRSS":
                combined_response[dof] = srss(modal_values)
            else:
                combined_response[dof] = _combine_cqc_with_rho(modal_values, rho_matrix)

        if method == "SRSS":
            combined_base_shear = srss(modal_base_shears)
            combined_otm = srss(modal_otms)
        else:
            combined_base_shear = _combine_cqc_with_rho(modal_base_shears, rho_matrix)
            combined_otm = _combine_cqc_with_rho(modal_otms, rho_matrix)

        return RSAResults(
            spectrum_periods=self.spectrum_periods[:],
            spectrum_accelerations=self.spectrum_accelerations[:],
            spectrum_values=spectrum_values,
            num_modes=len(modal_vectors),
            periods=periods,
            modal_response_vectors=modal_vectors,
            modal_base_shears=modal_base_shears,
            modal_overturning_moments=modal_otms,
            combination_method=method,
            combined_response=combined_response,
            combined_base_shear=combined_base_shear,
            combined_overturning_moment=combined_otm,
            rho_matrix=rho_matrix,
            damping_ratio=damping_ratio,
        )


def _rho_matrix(omegas: list, damping_ratio: float) -> list:
    return [[cqc_coefficient(oi, oj, damping_ratio) for oj in omegas] for oi in omegas]


def _combine_cqc_with_rho(values: list, rho: list) -> float:
    total = 0.0
    for i in range(len(values)):
        for j in range(len(values)):
            total += rho[i][j] * values[i] * values[j]
    return math.sqrt(max(total, 0.0))


def _mat_vec_mul(matrix: list, vector: list) -> list:
    return [sum(matrix[i][j] * vector[j] for j in range(len(vector))) for i in range(len(matrix))]
