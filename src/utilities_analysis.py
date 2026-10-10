import numpy as np

def statistics(x):

    x = np.array(x)                   # converts one col table to list

    # Non parametric statistics
    median = np.median(x)
    Q1 = np.percentile(x, 25)
    Q3 = np.percentile(x, 75)
    IQR = Q3 - Q1
    IQR_rel = IQR/median*100

   # Parametric statistics
    mean = np.mean(x)
    sd = np.std(x)
    thr = 3               # 3 sigma threshold
    z = (x - mean) / sd
    x_filtered = x[(z >= -thr) &  (z <= thr)]
    mean_filtered = np.mean(x_filtered)
    sd_filtered = np.std(x_filtered)

    stats = {
        'median' : median.item(),
        'iqr' : IQR.item(),
        'iqr_rel' : IQR_rel.item(),
        'mean' : mean_filtered.item(),      # mean is mean after 3 sigma filtering
        'sd' : sd_filtered.item(),
    }

    return stats