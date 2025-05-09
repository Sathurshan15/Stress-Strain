import numpy as np
import pandas as pd
from bayes_opt import BayesianOptimization
from sklearn.metrics import mean_squared_error

# Experimental Data
data = {
    "ε0": [0.002948676, 0.002948676, 0.002726779, 0.002764779, 0.001998479, 0.002680739, 0.00260141, 0.002892419, 0.002892419, 0.002784575, 0.003038907, 0.003241264, 0.002628701, 0.00299775, 0.003156578, 0.002628701, 0.00299775, 0.003156578, 0.002628701, 0.00299775, 0.003156578, 0.002628701, 0.00299775, 0.003156578, 0.002628701, 0.00299775, 0.003156578],
    "σp": [16.82, 16.11, 15.45, 13.54, 12.39, 10.43, 9.96, 16.02, 17.37, 14.29, 18.14, 21.53, 13.57, 18.36, 20.85, 13.49, 18.28, 20.77, 13.79, 18.58, 21.07, 12.8, 16.57, 18.53, 9.04, 12.18, 13.81],
    "Block Strength": [20.7, 16.2, 30.7, 13.1, 40.98, 23.4, 8.4, 18.4, 27.4, 16.8, 16.8, 16.8, 26.2, 26.2, 26.2, 25.7, 25.7, 25.7, 27.6, 27.6, 27.6, 24.4, 24.4, 24.4, 18.4, 18.4, 18.4],
    "Grout Strength": [30.34, 30.34, 21.9, 23.2, 6.2, 20.4, 21.3, 28, 28, 23.9, 34.7, 45, 18.8, 32.5, 40.3, 18.8, 32.5, 40.3, 18.8, 32.5, 40.3, 18.8, 32.5, 40.3, 18.8, 32.5, 40.3],
    "RMSE": [7.810819881, 7.288591408, 3.95650851, 1.989097411, 0.445139314, 1.653954842, 2.660086982, 7.471245562, 8.419362482, 6.238053704, 11.37249985, 13.23833052, 1.108814503, 2.39740507, 2.923506437, 3.467178031, 3.570424378, 5.422404994, 3.08040799, 3.436072071, 4.977721905, 0.606472497, 1.04308859, 0.769647037, 1.659003225, 2.084103252, 0.943475619]
}

df = pd.DataFrame(data)

# Stress-Strain Equation
def stress_strain_equation(ε, ε0, σp, A, B, C):
    return σp * (A * (ε / ε0)) / (B * (1.0 + C * (ε / ε0)) + (ε / ε0)**A)

def objective_function(A, B, C):
    # Penalty from exisiting equation from Zahra et al. 
    penalty_A = 100 * (A - 5)**2  
    penalty_B = 100 * (B - 5)**2  
    penalty_C = 1000 * (C - 0.01)**2  

    predicted_stress = []

    for i in range(len(df)):
        ε = np.linspace(0, 0.004, 100)  #  ε value
        σ_pred = stress_strain_equation(ε, df['ε0'][i], df['σp'][i], A, B, C)
        predicted_stress.append(σ_pred)  

    
    predicted_stress = np.array(predicted_stress)  
    mean_predicted_stress = np.mean(predicted_stress, axis=0)  
    actual_stress = np.full_like(mean_predicted_stress, np.mean(df['RMSE']))  
    rmse = np.sqrt(mean_squared_error(actual_stress, mean_predicted_stress))

    # Penalties to the RMSE
    total_penalty = penalty_A + penalty_B + penalty_C
    return -(rmse + total_penalty)  


# Define the bounds for A, B, and C
pbounds = {
    'A': (2, 8),  
    'B': (2, 8),  
    'C': (0.005, 0.02)  
}

# Initialize Bayesian Optimization
optimizer = BayesianOptimization(
    f=objective_function,
    pbounds=pbounds,
    random_state=42
)


optimizer.maximize(init_points=5, n_iter=25)
best_params = optimizer.max['params']
print("Best Parameters:", best_params)
