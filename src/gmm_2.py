import numpy as np
import pandas as pd
from  scipy.optimize import curve_fit


def _double_gaussian(x, a1, mu1, sigma1, a2, s, sigma2, c):
    """
    s ∈ [0, 1]  rescales δμ so that μ2 never exceeds 57.
    """
    delta_mu = 5.0 + (57.0 - mu1 - 5.0) * s    #   5 ≤ δμ ≤ 57–μ1
    mu2      = mu1 + delta_mu                  #   ⇒ μ2 ≤ 57
    g1 = a1 * np.exp(-(x - mu1) ** 2 / (2.0 * sigma1 ** 2))
    g2 = a2 * np.exp(-(x - mu2) ** 2 / (2.0 * sigma2 ** 2))
    return g1 + g2 + c


def gaussian_mixture_smooth_2(x, y, n=1000,
                            fit_window=(38.0, 58.0),
                            min_pts=10):
    """
    Returns
        x_new, y_smooth, y_raw, mu1, mu2
    """
    # ---------- prepare data ----------
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    lo, hi = fit_window
    mask   = (x >= lo) & (x <= hi)
    if mask.sum() < min_pts:
        raise ValueError(f"Only {mask.sum()} points in {fit_window}; "
                         f"need ≥{min_pts}.")
    x_fit, y_fit = x[mask], y[mask]

    # ---------- initial guesses ----------
    amp_guess = y_fit.max() - y_fit.min()
    mu1_guess = (lo + hi) / 2 - 5           # ~40
    sig_guess = max((hi - lo) / 10.0, 1.0)
    c_guess   = y_fit.min()

    p0 = [amp_guess/2,      # a1
          mu1_guess,        # μ1
          sig_guess,        # σ1
          amp_guess/2,      # a2
          0.5,              # s   (mid-range ⇒ δμ ≈ (5+max)/2)
          sig_guess,        # σ2
          c_guess]          # baseline

    # ---------- independent bounds ----------
    bounds_lo = [0.0,   37.0, 1e-3, 0.0, 0.0, 1e-3, -np.inf]   # s ≥ 0
    bounds_hi = [np.inf,52.0, np.inf, np.inf, 1.0, np.inf, np.inf]  # μ1 ≤ 52, s ≤ 1

    popt, _ = curve_fit(
        _double_gaussian,
        x_fit, y_fit,
        p0=p0,
        bounds=(bounds_lo, bounds_hi),
        maxfev=20_000
    )

    # ---------- evaluate curves ----------
    x_new  = np.linspace(x.min(), x.max(), n)
    y_new  = _double_gaussian(x_new, *popt)
    y_raw  = np.interp(x_new, x, y)

    # ---------- extract means ----------
    a1, mu1, _, a2, s_opt, _, _ = popt
    delta_mu = 5.0 + (57.0 - mu1 - 5.0) * s_opt
    mu2      = mu1 + delta_mu        # guaranteed ≤ 57

    rmse = float(np.sqrt(np.mean((y_fit - _double_gaussian(x_fit, *popt))**2)))

    return (pd.Series(x_new),
            pd.Series(y_new),
            pd.Series(y_raw),
            mu1,
            mu2,
            rmse)
