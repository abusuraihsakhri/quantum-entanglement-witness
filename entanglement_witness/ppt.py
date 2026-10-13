"""Validated two-qubit and qubit–qutrit Peres–Horodecki PPT analysis.

The PPT test is necessary and sufficient for separability in 2x2 and 2x3.
Input matrices are row-major in the computational product basis |a,b>.
JSON-compatible complex entries may be represented as [real, imaginary].
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np


class InvalidDensityMatrix(ValueError):
    """Raised for a state that is not a physical, supported density matrix."""


def _complex_entry(value: Any) -> complex:
    if isinstance(value, (list, tuple)):
        if len(value) != 2 or any(isinstance(x, (list, tuple, dict, bool)) for x in value):
            raise InvalidDensityMatrix("Complex entries must be [real, imaginary] numeric pairs")
        try:
            z = complex(float(value[0]), float(value[1]))
        except (TypeError, ValueError, OverflowError) as exc:
            raise InvalidDensityMatrix("Matrix entries must be numeric") from exc
    else:
        if isinstance(value, (str, dict, bool)):
            raise InvalidDensityMatrix("Matrix entries must be numbers or [real, imaginary] pairs")
        try:
            z = complex(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise InvalidDensityMatrix("Matrix entries must be numeric") from exc
    if not (np.isfinite(z.real) and np.isfinite(z.imag)):
        raise InvalidDensityMatrix("All matrix entries must be finite")
    return z


def _read_matrix(matrix: Sequence[Sequence[Any]], size: int) -> np.ndarray:
    try:
        if len(matrix) != size or any(len(row) != size for row in matrix):
            raise InvalidDensityMatrix(f"Expected a {size}x{size} matrix")
        return np.array([[_complex_entry(x) for x in row] for row in matrix], dtype=np.complex128)
    except (TypeError, KeyError) as exc:
        raise InvalidDensityMatrix("Matrix must be a square array of rows") from exc


def partial_transpose(matrix: np.ndarray, dimensions: tuple[int, int]) -> np.ndarray:
    """Partial transpose on subsystem B in product basis |a,b>."""
    a, b = dimensions
    return matrix.reshape(a, b, a, b).transpose(0, 3, 2, 1).reshape(a * b, a * b)


def _encode_matrix(matrix: np.ndarray) -> list[list[list[float]]]:
    return [[[float(z.real), float(z.imag)] for z in row] for row in matrix]


def analyze_density_matrix(
    matrix: Sequence[Sequence[Any]],
    dimensions: tuple[int, int] = (2, 2),
    tolerance: float = 1e-9,
) -> dict[str, Any]:
    """Return PPT eigenvalues, negativity and an NPT entanglement witness.

    This implementation accepts only 2x2 and 2x3 bipartite dimensions,
    where PPT positivity is both necessary and sufficient for separability.
    If negative eigenvalues are present, constructs W=(|v><v|)^(T_B)
    using the most-negative normalized partial-transpose eigenvector.
    """
    if not isinstance(dimensions, (list, tuple)) or tuple(dimensions) not in ((2, 2), (2, 3), (3, 2)):
        raise InvalidDensityMatrix("Supported subsystem dimensions are [2,2], [2,3] and [3,2]")
    if isinstance(tolerance, bool) or not np.isfinite(tolerance) or tolerance <= 0 or tolerance > 1e-5:
        raise ValueError("tolerance must be finite and between 0 and 1e-5")
    a, b = dimensions
    rho = _read_matrix(matrix, a * b)
    if not np.allclose(rho, rho.conj().T, rtol=0, atol=tolerance):
        raise InvalidDensityMatrix("Density matrix must be Hermitian")
    if not np.isclose(np.trace(rho), 1.0, rtol=0, atol=tolerance):
        raise InvalidDensityMatrix("Density matrix must have trace 1")
    state_eigenvalues = np.linalg.eigvalsh(rho)
    if float(state_eigenvalues[0]) < -tolerance:
        raise InvalidDensityMatrix("Density matrix must be positive semidefinite")

    pt = partial_transpose(rho, (a, b))
    eigenvalues, vectors = np.linalg.eigh(pt)
    negativity = float(np.maximum(-eigenvalues, 0.0).sum())
    npt = float(eigenvalues[0]) < -tolerance
    result: dict[str, Any] = {
        "dimensions": [a, b],
        "classification": "entangled" if npt else "separable",
        "criterion": "Peres–Horodecki PPT (complete for 2x2 and 2x3)",
        "partial_transpose_eigenvalues": [float(x) for x in eigenvalues],
        "minimum_eigenvalue": float(eigenvalues[0]),
        "negativity": negativity,
        "witness_expectation": None,
        "witness_matrix": None,
    }
    if npt:
        vec = vectors[:, 0]
        witness = partial_transpose(np.outer(vec, vec.conj()), (a, b))
        expectation = np.trace(witness @ rho)
        result["witness_expectation"] = float(expectation.real)
        result["witness_matrix"] = _encode_matrix(witness)
    return result
