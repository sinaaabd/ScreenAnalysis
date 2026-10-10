import numpy as np
import pandas as pd
from  scipy.optimize import curve_fit


# ────────────────────────────────────────────────────────────────────────────────
# 1.  Three-component Gaussian model
# ────────────────────────────────────────────────────────────────────────────────
def _triple_gaussian(x,
                     a1, mu1, sigma1,
                     a2, mu2, sigma2,
                     a3, mu3, sigma3,
                     c):
    """
    Sum of three normal densities + constant baseline.

    All three centres μk are *independently* constrained to the interval
    [30 , 58] by the bounds supplied to ``curve_fit`` (see below).
    """
    g1 = a1 * np.exp(-(x - mu1) ** 2 / (2.0 * sigma1 ** 2))
    g2 = a2 * np.exp(-(x - mu2) ** 2 / (2.0 * sigma2 ** 2))
    g3 = a3 * np.exp(-(x - mu3) ** 2 / (2.0 * sigma3 ** 2))
    return g1 + g2 + g3 + c


# ────────────────────────────────────────────────────────────────────────────────
# 2.  Smoother that enforces 30 ≤ μk ≤ 58 and returns a modelling error metric
# ────────────────────────────────────────────────────────────────────────────────
def gaussian_mixture_smooth(x, y, n: int = 1000,
                            fit_window: tuple = (30.0, 58.0),
                            min_pts: int = 10):
    """
    Smooth *y* over *x* with a **three-component** Gaussian mixture.

    Parameters
    ----------
    x, y : array-like
        Raw data to be smoothed.
    n : int, default 1000
        Number of points in the output grid.
    fit_window : (float, float), default (30.0, 58.0)
        Region in *x* used for the fit **and the allowed range for all μk**.
    min_pts : int, default 10
        Minimum number of points required in the fit_window.

    Returns
    -------
    x_new : pd.Series
        Regular grid spanning the full *x* domain.
    y_smooth : pd.Series
        Fitted mixture evaluated on *x_new*.
    y_raw : pd.Series
        Original *y* resampled onto *x_new* (via linear interpolation).
    mu1, mu2, mu3 : float
        Fitted centres of the three Gaussians.
    rmse : float
        **Root-mean-square fitting error** inside *fit_window*.
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
    span      = hi - lo
    mu1_guess = lo + span / 4.0
    mu2_guess = lo + span / 2.0
    mu3_guess = lo + 3.0 * span / 4.0
    sig_guess = max(span / 10.0, 1.0)
    c_guess   = y_fit.min()

    p0 = [amp_guess/3, mu1_guess, sig_guess,   # g1
          amp_guess/3, mu2_guess, sig_guess,   # g2
          amp_guess/3, mu3_guess, sig_guess,   # g3
          c_guess]                             # baseline

    # ---------- independent bounds (30 ≤ μk ≤ 58) ----------
    bounds_lo = [0.0,   30.0, 1e-3,
                 0.0,   30.0, 1e-3,
                 0.0,   30.0, 1e-3,
                -np.inf]

    bounds_hi = [np.inf, 58.0, np.inf,
                 np.inf, 58.0, np.inf,
                 np.inf, 58.0, np.inf,
                 np.inf]

    try:
        popt, _ = curve_fit(
            _triple_gaussian,
            x_fit, y_fit,
            p0=p0,
            bounds=(bounds_lo, bounds_hi),
            maxfev=30_000
        )
    except:
        print('Curve fit error')
        popt = [0] * 10

    # ---------- evaluate curves ----------
    x_new  = np.linspace(x.min(), x.max(), n)
    y_new  = _triple_gaussian(x_new, *popt)
    y_raw  = np.interp(x_new, x, y)

    # ---------- extract means & error ----------
    (_,  mu1, _,     # unpacking made explicit for clarity
     _,  mu2, _,
     _,  mu3, _,
     _) = popt

    rmse = float(np.sqrt(np.mean((y_fit - _triple_gaussian(x_fit, *popt))**2)))

    return (pd.Series(x_new),
            pd.Series(y_new),
            pd.Series(y_raw),
            mu1,
            mu2,
            mu3,
            rmse)
