import sys
import numpy as np

sys.path.append('..')
from src.sim import simulate_linear_disc, simulate_nonlinear
from src.controller.LQR import controllability, dlqr, dlqr_finite
from src.controller.koopman import koopman_control

    
def test_linear():
    A = np.array([[-0.8,0],[0,0.5]])
    B = np.array([[1],[1]])
    C = np.eye(2)
    u = np.zeros([1,100])
    x0 = np.array([[2],[1]])
    result = simulate_linear_disc(A,B,C,u,x0)
    assert np.linalg.norm(result[:, -1]) < 10**(-5), \
    "The state should go to zero"

def test_nonlinear():
    A = np.array([[-0.8,0],[0,0.5]])
    C = np.eye(2)
    x0 = np.array([[2],[1]])
    
    def f(x):
        return A @ x;
    
    def u(k, xk):
        return np.zeros([2,1])
    
    result = simulate_nonlinear(f, u, C, x0, 100)
    assert np.linalg.norm(result[:, -1]) < 10**(-5), \
            "The state should go to zero"
    
def test_controllability():
    A = np.array([[1,0],[0,2]])
    B = np.array([[1],[0]])
    R = controllability(A, B)
    
    assert np.linalg.matrix_rank(R) < 2, \
            "The system should be uncontrollable"

def test_dlqr():
    A = np.array([[1,2],[2,0]])
    B = np.array([[1],[0]])
    Q = np.array([[3,0],[0,1]])
    R = np.array([[2]])
    
    K = dlqr(A, B, Q, R)
    
    assert (np.linalg.norm(K - np.array([[1.1875, 1.9]])) / 
          np.linalg.norm(np.array([[1.1875, 1.9]])) < 10**-3), \
    "Calculation yields wrong result"

def test_dlqr_finite():
    A = np.array([[1,2],[2,0]])
    B = np.array([[1],[0]])
    Q = np.array([[3,0],[0,1]])
    R = np.array([[2]])
    
    Ks = dlqr_finite(A, B, Q, R, Q, 21)
    assert np.all(np.isclose(Ks[0], dlqr(A, B, Q, R))), \
    "Does not converge to dlqr when time horizon gets large"
    
def test_koopman():
    A = np.array([[1,2],[2,0]])
    B = np.array([[1],[0]])
    x0 = np.array([[2],[1]])
    C = np.eye(2)
    u = np.zeros([1,10])
    trajectory = simulate_linear_disc(A, B, C, u, x0)
    X = trajectory[:, 0:-1]
    Y = trajectory[:, 1:]
    assert np.all(np.isclose(koopman_control(X, Y, "PID"), A)), \
    "Linear dynamics should be learned perfectly"
