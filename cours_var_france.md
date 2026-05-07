# Cours Complet : Value-at-Risk (VaR)
### Appliquée aux Marchés Financiers Français

> **Niveau** : L3 Finance / M1 | **Actifs** : TotalEnergies (TTE.PA), CAC 40 (^FCHI), OAT France 10 ans

---

## TABLE DES MATIÈRES

1. [Fondements du risque de marché](#1-fondements-du-risque-de-marché)
2. [Rendements : simples vs log-rendements](#2-rendements--simples-vs-log-rendements)
3. [Définition mathématique de la VaR](#3-définition-mathématique-de-la-var)
4. [VaR Historique](#4-var-historique)
5. [VaR Paramétrique (Variance-Covariance)](#5-var-paramétrique-variance-covariance)
6. [VaR Monte Carlo](#6-var-monte-carlo)
7. [CVaR — Expected Shortfall](#7-cvar--expected-shortfall)
8. [Backtesting de Kupiec](#8-backtesting-de-kupiec)
9. [VaR d'un portefeuille multi-actifs](#9-var-dun-portefeuille-multi-actifs)
10. [Étude France : 3 actifs comparés](#10-étude-france--3-actifs-comparés)
11. [Limites de la VaR](#11-limites-de-la-var)
12. [Cheat Sheet VaR](#12-cheat-sheet-var)

---

## 1. Fondements du Risque de Marché

### 1.1 Définition du risque de marché

Le **risque de marché** est la possibilité de subir des pertes financières à cause de mouvements adverses des prix de marché : actions, taux d'intérêt, change, matières premières.

On distingue :
- **Risque directionnel** : la valeur d'un actif monte ou descend.
- **Risque de volatilité** : les fluctuations s'amplifient.
- **Risque de corrélation** : les actifs évoluent ensemble dans la mauvaise direction.
- **Risque de liquidité** : impossible de vendre sans impact de prix.

### 1.2 Pourquoi mesurer le risque ?

Les institutions financières (banques, fonds, assurances) ont besoin de :
- **Déterminer leurs fonds propres réglementaires** → Bâle III/IV impose un ratio minimum de capital couvrant la VaR.
- **Gérer les positions** → savoir combien on peut perdre avant d'agir.
- **Communiquer avec les investisseurs** → un chiffre simple et comparable.

> 💡 **Analogie** : La VaR est comme un thermomètre pour le risque. Elle ne prédit pas les crises, elle mesure la température normale du risque.

### 1.3 Horizon de calcul et niveau de confiance

Deux paramètres définissent toute VaR :

| Paramètre | Valeurs courantes | Exemple |
|-----------|------------------|---------|
| **Horizon T** | 1 jour (trading desk), 10 jours (régulation), 1 mois | 1 jour |
| **Niveau de confiance α** | 95%, 99%, 99.9% | 99% |

**Convention réglementaire Bâle III** : VaR 10 jours, 99%.
**Convention trading desk** : VaR 1 jour, 95%.

Pour passer d'un horizon à un autre (sous hypothèse de normalité et d'indépendance des rendements) :

```
VaR(T jours) = VaR(1 jour) × √T
```

> ⚠️ Cette règle de la racine carrée du temps n'est valide que si les rendements sont i.i.d. (indépendants et identiquement distribués). Elle sous-estime la VaR en cas de clustering de volatilité.

---

## 2. Rendements : Simples vs Log-rendements

### 2.1 Rendement simple

Pour un actif de prix P_t :

```
r_t = (P_t - P_{t-1}) / P_{t-1} = P_t / P_{t-1} - 1
```

**Avantage** : interprétation directe en pourcentage de gain/perte.
**Inconvénient** : non-additif dans le temps.

### 2.2 Log-rendement (rendement continu)

```
R_t = ln(P_t / P_{t-1}) = ln(P_t) - ln(P_{t-1})
```

**Avantages** :
- **Additif dans le temps** : R_{total} = R_1 + R_2 + ... + R_T
- Plus proche d'une loi normale → facilite les calculs analytiques.
- Symétrique : une hausse de 100% puis une baisse de 50% donne R_total = ln(2) + ln(0.5) = 0.

**Lien entre les deux** :
```
R_t ≈ r_t  pour de petites valeurs
R_t = ln(1 + r_t)
```

### 2.3 Pourquoi choisir l'un ou l'autre ?

| Contexte | Rendement recommandé |
|----------|---------------------|
| VaR historique | Simple ou log, peu importe |
| VaR paramétrique (normal) | **Log-rendement** (hypothèse de normalité) |
| Monte Carlo GBM | **Log-rendement** (par construction du modèle) |
| Performance de portefeuille | Simple (agrégation cross-sectionnelle) |

### 2.4 Statistiques descriptives essentielles

Avant tout calcul de VaR, calculer :

```
Moyenne μ = (1/T) Σ R_t
Variance σ² = (1/(T-1)) Σ (R_t - μ)²
Skewness = E[(R - μ)³] / σ³       (asymétrie)
Kurtosis excess = E[(R - μ)⁴] / σ⁴ - 3  (queues épaisses)
```

**Interprétation pour les actifs financiers :**
- Skewness < 0 → queue gauche épaisse → pertes extrêmes plus fréquentes que prévu.
- Kurtosis excess > 0 → **leptokurtique** → les chocs extrêmes arrivent plus souvent qu'une loi normale.

> 📌 Le CAC 40 a historiquement un kurtosis excédentaire ≈ 5-8. Cela signifie que la VaR normale **sous-estime** le risque réel.

---

## 3. Définition Mathématique de la VaR

### 3.1 Définition formelle

Soit L une variable aléatoire représentant la **perte** d'un portefeuille sur un horizon T (L > 0 = perte, L < 0 = gain).

```
VaR_α = inf { l ∈ ℝ : P(L > l) ≤ 1 - α }
      = F_L^{-1}(α)
```

En d'autres termes : **VaR_α est le quantile α de la distribution des pertes.**

**Exemple numérique** :
Portefeuille de 1 000 000 €, VaR 99% 1 jour = 25 000 €.
→ Il y a 99% de chances que la perte du jour ne dépasse pas 25 000 €.
→ Il y a 1% de chances qu'elle soit supérieure à 25 000 €.

### 3.2 P&L vs Pertes

Convention : on travaille souvent sur les **P&L** (Profit & Loss, positif = profit) :

```
VaR_α = -quantile_{1-α}(P&L)
       = quantile_α(Pertes)
```

Si on note X = P&L_t :
```
VaR_α = -Q_{1-α}(X)    où Q_{1-α} est le quantile de niveau (1-α)
```

Pour α = 95% : VaR = -5ème percentile de la distribution des P&L.
Pour α = 99% : VaR = -1er percentile de la distribution des P&L.

### 3.3 VaR en montant vs en pourcentage

```
VaR (EUR) = W × VaR (%)
```

Où W est la valeur du portefeuille.
Exemple : W = 50 EUR, VaR 95% = 5% → VaR = 2.50 EUR.

---

## 4. VaR Historique

### 4.1 Principe

La VaR historique est la méthode **non-paramétrique** la plus simple. Elle utilise directement les rendements passés observés.

**Hypothèse clé** : Le futur ressemblera au passé (distribution empirique = bonne approximation de la distribution future).

### 4.2 Algorithme étape par étape

```
Étape 1 : Collecter N rendements historiques r_1, r_2, ..., r_N
Étape 2 : Trier les rendements par ordre croissant
Étape 3 : VaR_α = -quantile_{1-α} de cette distribution
Étape 4 : Pour un horizon T > 1 : VaR_T = VaR_1 × √T  (approximation)
```

**En Python :**
```python
import numpy as np

returns = [...]  # liste des rendements quotidiens
var_95 = -np.percentile(returns, 5)   # 5ème percentile = quantile 5%
var_99 = -np.percentile(returns, 1)   # 1er percentile = quantile 1%
```

### 4.3 Exemple numérique

On dispose de 500 rendements quotidiens du CAC 40.
On les trie. Le 25ème plus mauvais (500 × 5% = 25) = -1.8%.
→ **VaR 95% = 1.8% par jour**.

Si le portefeuille vaut 10 000 € :
→ **VaR 95% = 180 € par jour**.

### 4.4 Avantages et inconvénients

| ✅ Avantages | ❌ Inconvénients |
|-------------|----------------|
| Aucune hypothèse de distribution | Dépend de la fenêtre choisie (250, 500, 1000 jours) |
| Capture les queues épaisses empiriquement | Ignore les événements hors échantillon |
| Simple à expliquer | Lent à réagir aux chocs récents |
| Pas de paramètres à estimer | Besoin de beaucoup de données |

### 4.5 Choix de la fenêtre

```
250 jours  → réactif mais peu stable, peu d'observations dans les queues
500 jours  → bon compromis
1000 jours → stable mais capte des régimes de marché très différents
```

> 💡 **Astuce quant** : Pour tester la robustesse, calculer la VaR sur plusieurs fenêtres et comparer les résultats. Un écart important signale une instabilité du risque.

---

## 5. VaR Paramétrique (Variance-Covariance)

### 5.1 Principe

On suppose que les log-rendements suivent une **loi normale** N(μ, σ²).

Alors la VaR s'exprime analytiquement :

```
VaR_α = -(μ - z_α × σ) × W
```

Où z_α est le quantile de la loi normale standard :
- z_95% = 1.645
- z_99% = 2.326
- z_99.9% = 3.090

### 5.2 Formule complète

Pour un portefeuille de valeur W, sur un horizon de 1 jour :

```
VaR_α (EUR) = W × (z_α × σ - μ)
```

En pratique, μ ≈ 0 pour 1 jour, donc :

```
VaR_α (EUR) ≈ W × z_α × σ
```

Pour 10 jours (Bâle) :
```
VaR_{10j} = VaR_{1j} × √10
```

### 5.3 Exemple numérique

TotalEnergies : σ_daily = 1.3%, μ_daily ≈ 0
Portefeuille W = 50 EUR

```
VaR 95% = 50 × 1.645 × 0.013 = 1.069 EUR
VaR 99% = 50 