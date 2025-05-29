from sklearn import metrics
from scipy.stats import norm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def log_roc(fpr: np.ndarray, tpr: np.ndarray, lam: float = 0.001, plot: bool = False):
    """
    Calculate log-adjusted ROC AUC
    See https://pubmed.ncbi.nlm.nih.gov/20735049/
    """
    # Ensure we start from lambda
    for i in range(len(fpr)):
        if fpr[i] > lam:
            # Linear interpolation to get value at lambda
            m = (tpr[i] - tpr[i - 1]) / (fpr[i] - fpr[i - 1])
            b = tpr[i] - m * fpr[i]
            fpr = np.array([lam] + list(fpr[i:]))
            tpr = np.array([m * lam + b] + list(tpr[i:]))
            break
        elif fpr[i] == lam:
            fpr = fpr[i:]
            tpr = tpr[i:]
            break
    else:
        # If we never find a point >= lambda, return NaN
        return float('nan')
    
    # Remove duplicate FPR values
    idx = np.array(list(fpr[:-1] != fpr[1:]) + [True])
    fpr = fpr[idx]
    tpr = tpr[idx]
    
    # Calculate log-adjusted AUC
    b = tpr[1:] - fpr[1:] * (tpr[1:] - tpr[:-1]) / (fpr[1:] - fpr[:-1])
    auc = np.sum((tpr[1:] - tpr[:-1]) / np.log(10))
    auc += np.sum(b * (np.log10(fpr[1:]) - np.log10(fpr[:-1])))
    auc /= np.log10(1 / lam)
    auc -= 0.14462
    
    if plot:
        plt.figure(figsize=(8, 6))
        plt.plot(np.log10(fpr), tpr)
        plt.xlabel('log10(FPR)')
        plt.ylabel('TPR')
        plt.title('Log-adjusted ROC Curve')
        plt.grid(True)
        plt.show()
    
    return auc

def enrichment_factor(y_true, y_scores, fraction=0.01):
    """
    Calculate enrichment factor at given fraction
    """
    # Sort by scores (descending for energies, use negative if lower is better)
    idx = np.argsort(-y_scores)
    y_true_sorted = y_true[idx]
    
    n_selected = int(fraction * len(y_true))
    if n_selected == 0:
        return float('nan')
    
    hit_rate = y_true_sorted[:n_selected].mean()
    base_rate = y_true.mean()
    
    if base_rate == 0:
        return float('nan')
    
    return hit_rate / base_rate

def calculate_roc_from_energies(y_true, energies, lower_is_better=True, plot_roc=False, plot_log_roc=False):
    """
    Calculate ROC metrics directly from energy predictions and binary labels
    
    Parameters:
    -----------
    y_true : array-like
        Binary labels (1 for active/positive, 0 for inactive/negative)
    energies : array-like
        Predicted energies
    lower_is_better : bool
        If True, lower energies indicate better predictions (typical for binding energies)
    plot_roc : bool
        Whether to plot standard ROC curve
    plot_log_roc : bool
        Whether to plot log-adjusted ROC curve
    
    Returns:
    --------
    dict with metrics: auc, log_auc, ef1, ef5, ef10
    """
    y_true = np.array(y_true)
    energies = np.array(energies)
    
    # Handle missing values
    mask = ~(np.isnan(energies) | np.isinf(energies))
    y_true = y_true[mask]
    energies = energies[mask]
    
    if len(np.unique(y_true)) < 2:
        print("Warning: Only one class present in labels")
        return {
            'auc': float('nan'),
            'log_auc': float('nan'),
            'ef1': float('nan'),
            'ef5': float('nan'),
            'ef10': float('nan'),
            'n_pos': sum(y_true == 1),
            'n_neg': sum(y_true == 0)
        }
    
    # Convert energies to scores (higher score = better prediction)
    if lower_is_better:
        scores = -energies
    else:
        scores = energies
    
    # Calculate ROC curve
    fpr, tpr, thresholds = metrics.roc_curve(y_true, scores)
    
    # Standard AUC
    auc = metrics.auc(fpr, tpr)
    
    # Log-adjusted AUC
    log_auc = log_roc(fpr, tpr, plot=plot_log_roc)
    
    # Enrichment factors
    ef1 = enrichment_factor(y_true, scores, fraction=0.01)
    ef5 = enrichment_factor(y_true, scores, fraction=0.05)
    ef10 = enrichment_factor(y_true, scores, fraction=0.10)
    
    # Plot standard ROC if requested
    if plot_roc:
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc:.3f})')
        plt.plot([0, 1], [0, 1], 'k--', label='Random')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC Curve')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    return {
        'auc': auc,
        'log_auc': log_auc,
        'ef1': ef1,
        'ef5': ef5,
        'ef10': ef10,
        'n_pos': sum(y_true == 1),
        'n_neg': sum(y_true == 0)
    }
