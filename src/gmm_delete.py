import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

# ---------------------------------------------------------------------
#  Two-Gaussian model
# ---------------------------------------------------------------------
def _double_gaussian(x, a1, mu1, sigma1, a2, delta_mu, sigma2, c):
    mu2 = mu1 + delta_mu
    g1 = a1 * np.exp(-(x - mu1) ** 2 / (2.0 * sigma1 ** 2))
    g2 = a2 * np.exp(-(x - mu2) ** 2 / (2.0 * sigma2 ** 2))
    return g1 + g2 + c


# ---------------------------------------------------------------------
#  PUBLIC FUNCTION  (returns μ₁ and μ₂ as the 3rd and 4th items)
# ---------------------------------------------------------------------
def gaussian_mixture_smooth(x, y, n=500,
                            fit_window=(38.0, 57.0),
                            min_pts=10):
    """
    Fit a constrained two-Gaussian mixture to (x, y), ignoring data
    outside *fit_window*.

    Returns
    -------
    x_new : pandas.Series   – n evenly spaced x-points
    y_new : pandas.Series   – smoothed curve at those x-points
    mu1   : float           – mean of the first Gaussian (≤ μ₂)
    mu2   : float           – mean of the second Gaussian
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    # 1) Keep only points inside the fitting window
    lo, hi = fit_window
    mask = (x >= lo) & (x <= hi)
    if mask.sum() < min_pts:
        raise ValueError(f"Only {mask.sum()} points inside {fit_window}; "
                         f"need at least {min_pts}.")
    x_fit, y_fit = x[mask], y[mask]

    # 2) Initial guesses
    amp_guess = y_fit.max() - y_fit.min()
    mu1_guess = 45        # e.g. ~40
    mu2_guess = 55        # e.g. ~56
    sig_guess = max((hi - lo) / 10.0, 1.0)
    c_guess   = y_fit.min()

    p0 = [amp_guess / 2,           # a1
          mu1_guess,               # μ1
          sig_guess,               # σ1
          amp_guess / 2,           # a2
          mu2_guess - mu1_guess,   # δμ
          sig_guess,               # σ2
          c_guess]                 # baseline

    # 3) Bounds that enforce your three rules
    bounds_lo = [0.0,     37.0, 1e-3,   0.0,    3.0,  1e-3,  -np.inf]
    bounds_hi = [np.inf,  53.0, np.inf, np.inf, 15.0, np.inf, np.inf]

    popt, _ = curve_fit(
        _double_gaussian,
        x_fit, y_fit,
        p0=p0,
        bounds=(bounds_lo, bounds_hi),
        maxfev=20_000
    )

    # 4) Evaluate fitted curve
    x_new = np.linspace(x.min(), x.max(), n)
    y_new = _double_gaussian(x_new, *popt)

    # Extract means
    mu1 = popt[1]                 # μ₁
    mu2 = mu1 + popt[4]           # μ₂ = μ₁ + δμ

    y_raw = np.interp(x_new, x, y)

    return pd.Series(x_new), pd.Series(y_new), pd.Series(y_raw), mu1, mu2
