import math
import numpy as np
import pytest
from entanglement_witness.ppt import analyze_density_matrix, InvalidDensityMatrix


def test_bell_state_gives_negative_partial_transpose_and_witness():
    bell = np.array([1, 0, 0, 1], dtype=complex) / math.sqrt(2)
    rho = np.outer(bell, bell.conj())
    result = analyze_density_matrix(rho.tolist())
    assert result["classification"] == "entangled"
    assert result["partial_transpose_eigenvalues"] == pytest.approx([-0.5, 0.5, 0.5, 0.5])
    assert result["negativity"] == pytest.approx(0.5)
    assert result["witness_expectation"] == pytest.approx(-0.5)
    witness = np.array([[complex(*entry) for entry in row] for row in result["witness_matrix"]])
    assert np.trace(witness @ rho).real == pytest.approx(-0.5)
    assert np.allclose(witness, witness.conj().T)


def test_separable_product_and_mixed_states():
    zero_zero = [[1,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    for rho in (zero_zero, (np.eye(4)/4).tolist()):
        result = analyze_density_matrix(rho)
        assert result["classification"] == "separable"
        assert result["negativity"] == pytest.approx(0)
        assert result["witness_matrix"] is None


def test_complex_bell_state():
    vec = np.array([1, 0, 0, 1j]) / math.sqrt(2)
    rho = np.outer(vec, vec.conj())
    pairs = [[[float(z.real), float(z.imag)] for z in row] for row in rho]
    result = analyze_density_matrix(pairs)
    assert result["negativity"] == pytest.approx(0.5)
    assert result["witness_expectation"] == pytest.approx(-0.5)


def test_qubit_qutrit_and_subsystem_order():
    vec = np.zeros(6, dtype=complex)
    vec[0] = vec[4] = 1/math.sqrt(2)
    rho = np.outer(vec, vec.conj())
    assert analyze_density_matrix(rho.tolist(), dimensions=(2,3))["negativity"] == pytest.approx(0.5)
    perm = np.arange(6).reshape(2,3).T.reshape(-1)
    rho2 = rho[np.ix_(perm, perm)]
    assert analyze_density_matrix(rho2.tolist(), dimensions=(3,2))["negativity"] == pytest.approx(0.5)


@pytest.mark.parametrize("matrix,match", [
    ([[1,0],[0,0]], "4x4"),
    (np.diag([1.1,-0.1,0,0]).tolist(), "positive semidefinite"),
    (np.diag([0.8,0,0,0]).tolist(), "trace 1"),
    ([[1,1,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]], "Hermitian"),
    ([[float("nan"),0,0,0]] + [[0]*4 for _ in range(3)], "finite"),
])
def test_invalid_states_are_rejected(matrix,match):
    with pytest.raises(InvalidDensityMatrix, match=match):
        analyze_density_matrix(matrix)


def test_unsupported_dimensions():
    with pytest.raises(InvalidDensityMatrix, match="Supported"):
        analyze_density_matrix(np.eye(9).tolist(), dimensions=(3,3))
