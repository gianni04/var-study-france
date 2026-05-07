import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import os

os.makedirs("output", exist_ok=True)

# =============================================================
# CONFIGURATION GENERALE
# =============================================================

# Actifs (France)
TICKERS = {
    "Action_TotalEnergies": "TTE.PA",   # Action française
    "Indice_CAC40": "^FCHI",           # Indice CAC 40
    # Pour l'obligation, on utilise ici un ETF obligataire France (proxy) si dispo
    # ou à défaut on pourra insérer une série de rendement 10Y France via CSV externe
}

START = "2018-01-01"  # au moins 5 ans d'historique
END   = None           # None = jusqu'à aujourd"hui

CAPITAL = 100_000      # capital de référence pour la VaR (en EUR)
CONF_LEVELS = [0.95, 0.99]

print("Projet VaR France - téléchargement des données...")

# =============================================================
# FONCTIONS UTILITAIRES
# =============================================================

def download_prices(tickers: dict, start: str, end: str = None) -> pd.DataFrame:
    data = {}
    for name, ticker in tickers.items():
        print(f"Téléchargement: {name} ({ticker})")
        px = yf.download(ticker, start=start, end=end, auto_adjust=True)["Close"].dropna()
        data[name] = px
    df = pd.DataFrame(data)
    return df


def compute_returns(df_prices: pd.DataFrame, log_returns: bool = True) -> pd.DataFrame:
    if log_returns:
        rets = np.log(df_prices / df_prices.shift(1))
    else:
        rets = df_prices.pct_change()
    return rets.dropna()


def var_historique(pnl: pd.Series, alpha: float) -> float:
    # alpha = niveau de confiance (ex: 0.95) => quantile 1-alpha des pertes
    # On suppose pnl en EUR, positif/gagnant, négatif/perte
    sorted_losses = -pnl.sort_values()  # pertes positives
    q = np.quantile(sorted_losses, 1 - alpha)
    return q


def es_historique(pnl: pd.Series, alpha: float) -> float:
    sorted_losses = -pnl.sort_values()
    var_level = np.quantile(sorted_losses, 1 - alpha)
    tail = sorted_losses[sorted_losses >= var_level]
    if len(tail) == 0:
        return np.nan
    return tail.mean()


def var_param_gaussienne(pnl: pd.Series, alpha: float) -> float:
    mu = pnl.mean()
    sigma = pnl.std(ddof=1)
    z = stats.norm.ppf(alpha)
    # VaR en tant que perte positive
    return max(0.0, -(mu - z * sigma))


def es_param_gaussienne(pnl: pd.Series, alpha: float) -> float:
    mu = pnl.mean()
    sigma = pnl.std(ddof=1)
    z = stats.norm.ppf(alpha)
    # ES pour une loi normale
    pdf = stats.norm.pdf(z)
    es = -(mu - sigma * pdf / (1 - alpha))
    return max(0.0, es)


def backtest_var_kupiec(real_pnl: pd.Series, var_series: pd.Series, alpha: float):
    """Retourne (n_exceptions, LR_PoF, p_value)"""
    # Exceptions: jours où la perte réelle dépasse la VaR (perte > VaR)
    losses = -real_pnl
    exceptions = losses > var_series
    n_f = exceptions.sum()
    T = len(exceptions)
    p = 1 - alpha
    if T == 0:
        return 0, np.nan, np.nan
    # Probabilité sous H0
    if n_f == 0 or n_f == T:
        # éviter log(0)
        return n_f, np.nan, np.nan
    num = ((1 - p) ** (T - n_f)) * (p ** n_f)
    phat = n_f / T
    den = ((1 - phat) ** (T - n_f)) * (phat ** n_f)
    LR = -2 * np.log(num / den)
    p_value = 1 - stats.chi2.cdf(LR, df=1)
    return int(n_f), float(LR), float(p_value)


# =============================================================
# 1. TELECHARGEMENT & PREPARATION
# =============================================================

prices = download_prices(TICKERS, START, END)
returns = compute_returns(prices, log_returns=True)

print("\nDimensions des données:")
print("Prices:", prices.shape)
print("Returns:", returns.shape)

# On suppose une position de CAPTIAL entièrement investie dans chaque actif
# Valeur du portefeuille pour actif i: P_i = CAPITAL

# P&L journalier en EUR pour chaque actif: PNL_i,t = CAPITAL * R_i,t
pnl = returns * CAPITAL

# =============================================================
# 2. CALCUL VAR / ES POUR CHAQUE ACTIF
# =============================================================

results = []

for name in pnl.columns:
    pnl_series = pnl[name].dropna()
    print(f"\n===== {name} =====")
    for alpha in CONF_LEVELS:
        var_hist = var_historique(pnl_series, alpha)
        es_hist = es_historique(pnl_series, alpha)
        var_gauss = var_param_gaussienne(pnl_series, alpha)
        es_gauss = es_param_gaussienne(pnl_series, alpha)
        print(f"VaR hist {int(alpha*100)}%: {var_hist:,.2f} EUR | ES hist: {es_hist:,.2f} EUR")
        print(f"VaR gauss {int(alpha*100)}%: {var_gauss:,.2f} EUR | ES gauss: {es_gauss:,.2f} EUR")
        results.append({
            "Actif": name,
            "Alpha": alpha,
            "VaR_hist": var_hist,
            "ES_hist": es_hist,
            "VaR_gauss": var_gauss,
            "ES_gauss": es_gauss,
        })

results_df = pd.DataFrame(results)
results_df.to_csv("output/var_es_summary.csv", index=False)
print("\nRésumé VaR/ES sauvegardé dans output/var_es_summary.csv")

# =============================================================
# 3. BACKTESTING SIMPLE SUR FENETRE ROLLING
# =============================================================

WINDOW = 250  # env. 1 an

backtest_rows = []

for name in pnl.columns:
    pnl_series = pnl[name].dropna()
    dates = pnl_series.index
    print(f"\nBacktesting VaR historique pour {name}...")
    for alpha in CONF_LEVELS:
        var_series = []
        var_index = []
        for i in range(WINDOW, len(pnl_series)):
            window_pnl = pnl_series.iloc[i-WINDOW:i]
            var_i = var_historique(window_pnl, alpha)
            var_series.append(var_i)
            var_index.append(dates[i])
        var_series = pd.Series(var_series, index=var_index)
        aligned_pnl = pnl_series.loc[var_series.index]
        n_exc, lr_pof, p_val = backtest_var_kupiec(aligned_pnl, var_series, alpha)
        print(f"Alpha {int(alpha*100)}% | Exceptions: {n_exc} / {len(aligned_pnl)} | LR={lr_pof:.3f} | p-value={p_val:.3f}")
        backtest_rows.append({
            "Actif": name,
            "Alpha": alpha,
            "Exceptions": n_exc,
            "T": len(aligned_pnl),
            "LR_PoF": lr_pof,
            "p_value": p_val,
        })

backtest_df = pd.DataFrame(backtest_rows)
backtest_df.to_csv("output/backtest_kupiec_summary.csv", index=False)
print("\nRésumé backtesting (Kupiec) sauvegardé dans output/backtest_kupiec_summary.csv")

# =============================================================
# 4. CHARTS SIMPLES (DISTRIBUTION + VAR)
# =============================================================

for name in pnl.columns:
    pnl_series = pnl[name].dropna()
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=pnl_series, nbinsx=80,
                               name="P&L journalier",
                               marker_color="steelblue", opacity=0.7))
    for alpha, color in zip(CONF_LEVELS, ["orange", "red"]):
        var_h = var_historique(pnl_series, alpha)
        fig.add_vline(x=-var_h, line_color=color, line_dash="dash", line_width=2,
                      annotation_text=f"VaR hist {int(alpha*100)}%: {var_h:,.0f} EUR",
                      annotation_position="top left")
    fig.update_layout(title=f"Distribution P&L journalier - {name}",
                      xaxis_title="P&L (EUR)", yaxis_title="Fréquence",
                      template="plotly_dark")
    outfile = f"output/histo_pnl_{name}.html"
    fig.write_html(outfile)
    print(f"Graphique sauvegardé: {outfile}")

print("\n=== Fin du script main.py (VaR France) ===")
