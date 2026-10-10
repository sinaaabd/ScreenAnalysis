import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

# ────────────────────────────────────────────────────────────────────────────────
# 1) Three-component Gaussian with constrained gaps (>5) via reparameterization
# ────────────────────────────────────────────────────────────────────────────────
def _triple_gaussian_gapped(x,
                            a1, mu1, sigma1,
                            a2, d12, sigma2,
                            a3, d23, sigma3,
                            c):
    """
    Sum of three Gaussians + constant, with enforced gaps:
        mu2 = mu1 + 5 + exp(d12)
        mu3 = mu2 + 5 + exp(d23)
    """
    mu2 = mu1 + 5.0 + np.exp(d12)
    mu3 = mu2 + 5.0 + np.exp(d23)

    g1 = a1 * np.exp(-(x - mu1)**2 / (2.0 * sigma1**2))
    g2 = a2 * np.exp(-(x - mu2)**2 / (2.0 * sigma2**2))
    g3 = a3 * np.exp(-(x - mu3)**2 / (2.0 * sigma3**2))
    return g1 + g2 + g3 + c

# ────────────────────────────────────────────────────────────────────────────────
# 2) Smoother using the gapped parameterization
# ────────────────────────────────────────────────────────────────────────────────
def gaussian_mixture_smooth_3(x, y, n: int = 1000,
                            fit_window: tuple = (30.0, 58.0),
                            min_pts: int = 10):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    lo, hi = fit_window
    mask   = (x >= lo) & (x <= hi)
    if mask.sum() < min_pts:
        raise ValueError(f"Only {mask.sum()} points in {fit_window}; need ≥{min_pts}.")
    x_fit, y_fit = x[mask], y[mask]

    # ---------- initial guesses ----------
    amp_guess = y_fit.max() - y_fit.min()
    span      = hi - lo
    # Choose mu1 so that mu2 and mu3 can fit with the mandatory gaps
    mu1_guess = max(lo, hi - 10 - span/2)  # a reasonable interior start
    mu2_guess = mu1_guess + span/3
    mu3_guess = mu1_guess + 2*span/3
    # Convert to d12/d23 (inverse of our transform):
    d12_guess = np.log(max(mu2_guess - mu1_guess - 5.0, 1.0))  # positive inside log
    d23_guess = np.log(max(mu3_guess - mu2_guess - 5.0, 1.0))

    sig_guess = max(span / 10.0, 1.0)
    c_guess   = y_fit.min()

    p0 = [amp_guess/3, mu1_guess, sig_guess,   # a1, mu1, sigma1
          amp_guess/3, d12_guess, sig_guess,   # a2, d12, sigma2
          amp_guess/3, d23_guess, sig_guess,   # a3, d23, sigma3
          c_guess]                              # baseline

    # ---------- bounds ----------
    # mu1 must leave room for two >5 gaps: mu1 ≤ hi - 10 = 48 in your case.
    bounds_lo = [0.0,   lo,   1e-3,
                 0.0,  -np.inf, 1e-3,
                 0.0,  -np.inf, 1e-3,
                 -np.inf]

    bounds_hi = [np.inf, hi - 10.0, np.inf,
                 np.inf,  np.inf,   np.inf,
                 np.inf,  np.inf,   np.inf,
                 np.inf]

    try:
        popt, _ = curve_fit(
            _triple_gaussian_gapped,
            x_fit, y_fit,
            p0=p0,
            bounds=(bounds_lo, bounds_hi),
            maxfev=30_000
        )
    except Exception as e:
        print(f'Curve fit error: {e}')
        popt = [0]*10

    # ---------- evaluate curves ----------
    x_new = np.linspace(x.min(), x.max(), n)
    y_new = _triple_gaussian_gapped(x_new, *popt)
    y_raw = np.interp(x_new, x, y)

    # ---------- extract actual means ----------
    _, mu1, _, _, d12, _, _, d23, _, _ = popt
    mu2 = mu1 + 5.0 + np.exp(d12)
    mu3 = mu2 + 5.0 + np.exp(d23)

    rmse = float(np.sqrt(np.mean(
        (y_fit - _triple_gaussian_gapped(x_fit, *popt))**2
    )))

    return (pd.Series(x_new),
            pd.Series(y_new),
            pd.Series(y_raw),
            float(mu1), float(mu2), float(mu3),
            rmse)
