# Getting started
## Installation
Navigate into the git repository.
Create a new python virtual environment:
```bash
python -m venv .venv
```
Activate the virtual environment:
```bash
.venv\Scripts\activate
```
You should now see `(.venv)` in the terminal, indicating that the environment is active.

With the environment active, install the required python packages:
```bash
python -m pip install -r requirements.txt
```
That's it.

## Running the main script
Make sure the virtual environment `(.venv)` is active.
Run
```bash
python main.py
```

# Formulas
## Compound interest

$K_0$: initial balance,
$K_l$: balance after $l$ contributions,
$r$: annual interest rate,
$m$: regular contribution,
$P$: contributions per year,
$N$: years,
$K_{NP}$: final balance

We convert the annual interest rate to an interest rate per contribution period:
```math
    r_P = (1 + r)^{\frac{1}{P}}.
```
The balance after $l$ contribution periods is
```math
    K_{l+1} = K_l r_P + m.
```
We can express $K_l$ by means of the initial $K_0$:
```math
\begin{align*}
    K_1 &= K_0 \cdot r_P + m \\
    K_2 &= K_1 \cdot r_P + m
        = (K_0 r_P + m) r_p + m
        = K_0 r_P^2 + m (1 + r_P) \\
    K_3 &= K_2 \cdot r_P + m
        = (K_0 r_P^2 + m (1 + r_P)) r_P + m
        = K_0 r_P^3 + m (1 + r_P + r_P^2) \\
    &\vdots\\
    K_l &= K_0 r_P^l + m \sum_{i=0}^{l-1} r_P^i
        = K_0 r_P^l + m \frac{1 - r_P^l}{1 - r_P}
\end{align*}
```
Thus, the final balance is given by
```math
    K_{NP} = K_0 (1 + r)^N + m \frac{1 - (1 + r)^N}{1 - (1 + r)^{\frac{1}{P}}}.
```
Note that we already plugged in $r_P = (1 + r)^{\frac{1}{P}}$.
The formula is implemented in `compound_interest`.

### Interest rate needed for a given final balance
Using the abbreviation $R = 1 + r$, we get
```math
    K_{NP} = K_0 R^N + m \frac{1 - R^N}{1 - R^{\frac{1}{P}}}.
```
From this, we derive a polynomial in $S = R^{\frac{1}{P}}$:
```math
\begin{align}
    &K_{NP} = K_0 S^{NP} + m \frac{1 - S^{NP}}{1 - S} \\
    &\Leftrightarrow\, (1 - S) K_{NP} = (1 - S) K_0 S^{NP} + m (1 - S^{NP}) \\
    &\Leftrightarrow\, K_{NP} - S K_{NP} = K_0 S^{NP} - K_0 S^{NP + 1} + m - m S^{NP} \\
    &\Leftrightarrow\, 0 = -K_{NP} + S K_{NP} + K_0 S^{NP} - K_0 S^{NP + 1} + m - m S^{NP} \\
    &\Leftrightarrow\, 0 = S^{NP + 1} (-K_0) + S^{NP} (K_0 - m) + S K_{NP} + (m - K_{NP})
\end{align}
```
As a result, finding the interest rate $\tilde{r}$ which leads to a given final balance $K_{NP}$
amounts to finding a suitable root $\tilde{S}$ of the polynomial
and computing $\tilde{r} = \tilde{S}^P - 1$.
This is implemented in the function `compound_interest_rate`.
