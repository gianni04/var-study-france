# Cours complet : Value-at-Risk (VaR) – Étude France (Action, Indice, Obligation)

> Projet pédagogique complet appliqué à trois actifs français : **TotalEnergies (action)**, **CAC 40 (indice)** et **OAT France 10 ans (obligation)**.

---

## 1. Intuition générale du risque de marché

### 1.1. Qu’est‑ce que le risque de marché ?

Le risque de marché, c’est le risque de perte sur un portefeuille lié aux variations défavorables des prix des actifs (actions, obligations, indices, FX, matières premières, etc.).[web:145]  
Il se matérialise sous forme de **distribution de rendements** : certaines journées sont légèrement gagnantes ou perdantes, et plus rarement on observe de très fortes pertes ou gains (queues de distribution, ou *tails*).[web:153]

### 1.2. Idée de la Value‑at‑Risk (VaR)

La **Value‑at‑Risk (VaR)** d’un portefeuille est une **perte potentielle maximale** sur un horizon donné, pour un **niveau de confiance** fixé.[web:153]  
Exemple : « VaR 1 jour, 95 % = 1 M€ » signifie : 
- avec 95 % de probabilité, la perte **ne dépassera pas** 1 M€ sur 1 jour,
- il reste 5 % de cas (les pires 5 %) où la perte **peut dépasser** 1 M€.[web:145]

La VaR est donc un **quantile de la distribution de pertes** :
- VaR 95 % = quantile 5 % des pertes (ou quantile 5 % des rendements, avec signe adapté),
- VaR 99 % = quantile 1 % des pertes.[web:153]

### 1.3. Horizon temporel et niveau de confiance

On doit toujours préciser :
- l’**horizon** : typiquement 1 jour, 10 jours (Bâle) ou 1 mois,
- le **niveau de confiance** : souvent 95 %, 97.5 % ou 99 %.[web:151]

En pratique :
- **moins l’horizon est long**, plus la VaR est faible mais plus il y a de bruit quotidien,
- **plus le niveau de confiance est élevé**, plus la VaR est élevée (on protège une queue plus extrême).[web:145]

---

## 2. Rendements, P&L et choix des données

### 2.1. Rendement simple vs log‑rendement

Soit un prix \(S_t\) et \(S_{t-1}\) :
- **rendement simple** : \(R_t = \frac{S_t - S_{t-1}}{S_{t-1}}\),
- **log‑rendement** : \(r_t = \ln(S_t) - \ln(S_{t-1}) = \ln\left(\frac{S_t}{S_{t-1}}\right)\).[web:153]

En risque de marché :
- les log‑rendements sont **additifs dans le temps** (somme de log‑rendements = log du ratio de prix),
- ils sont souvent plus « symétriques » et mieux adaptés à des hypothèses gaussiennes ou Student‑t.[web:153]

### 2.2. Construction du P&L

Pour un actif avec position \(w\) (nombre d’unités, ou valeur en monnaie), le **P&L** sur un jour :\(\Delta P_t = w \cdot R_t\).  
Pour un portefeuille multi‑actifs \(i = 1,\dots,n\) : \(\Delta P_t = \sum_i w_i R_{i,t}\).[web:145]

La VaR sera calculée sur la distribution empirique estimée de \(\Delta P_t\) (VaR historique) ou sur une approximation paramétrique de cette distribution (VaR gaussienne, Student‑t, etc.).[web:153]

### 2.3. Actifs de l’étude France

On fixe trois actifs représentatifs :
- **Action** : TotalEnergies (ticker Euronext : `TTE.PA`),
- **Indice** : CAC 40 (ticker `^FCHI` sur la plupart des fournisseurs de données),
- **Obligation** : OAT France 10 ans, approchée via son **rendement de marché 10Y France**.[web:148][web:152]

Les rendements des actions et de l’indice seront calculés à partir des prix ajustés.  
Pour l’obligation, plusieurs approches sont possibles :
- soit on construit un **prix obligataire** théorique à partir du rendement 10Y (plus lourd),
- soit on travaille directement sur la **variation du rendement** comme proxy de P&L directionnel (simplifié mais pédagogique).[web:148]

---

## 3. Définition mathématique de la VaR

### 3.1. VaR comme quantile

Soit \(L\) la **perte** (positive quand on perd de l’argent).  
La VaR au niveau de confiance \(\alpha\) (par ex. 95 %) est définie comme :
\[ \text{VaR}_\alpha = \inf\{ \ell \in \mathbb{R} : \mathbb{P}(L \le \ell) \ge \alpha \}. \]  
En pratique :
- VaR 95 % = perte telle que **95 % du temps la perte est inférieure** à cette valeur,
- les **5 % restants** sont les cas où la perte dépasse la VaR.[web:145][web:153]

Si on travaille en rendements \(R\) (positifs ou négatifs) plutôt qu’en pertes :
- on prend le **quantile \(1-\alpha\)** des rendements,
- puis on le convertit en perte monétaire sur la position. [web:153]

### 3.2. VaR absolue vs relative

- **VaR absolue** : perte en valeur monétaire (ex : « VaR 95 % = 1 M€ »),
- **VaR relative** : perte par rapport à l’espérance (ou au 0) — parfois exprimée en pourcentage.[web:145]

Dans ce cours, on travaillera principalement en **VaR absolue** sur un capital donné (par ex. 1 M€ ou 50 k€) et sur un horizon 1 jour ou 10 jours.

### 3.3. VaR et capital réglementaire

Les régulateurs (Bâle II/III) ont historiquement utilisé la VaR (10 jours, 99 %) comme base pour le calcul du **capital économique** pour risque de marché.[web:151]  
Cependant, ils ont progressivement migré vers l’**Expected Shortfall (ES)** pour mieux capter les pertes extrêmes en période de stress, car la VaR ne dit **rien sur la gravité des pertes au‑delà du quantile**. [web:151][web:145]

---

## 4. VaR historique

### 4.1. Principe

La **VaR historique** repose directement sur les **données passées** : 
- on collecte une série de rendements historiques \(R_1, \dots, R_T\),
- on calcule le P&L sur le portefeuille pour chaque jour,
- on trie les P&L du plus mauvais au meilleur,
- la VaR \(\alpha\) est le **quantile empirique** correspondant.[web:153]

Exemple (VaR 95 %, 1 jour, 1000 observations) :
- on ordonne les 1000 P&L,
- la VaR (perte) est la 50‑ème pire observation (5 % de 1000 = 50).

### 4.2. Avantages et limites

**Avantages :**
- ne nécessite aucune hypothèse paramétrique (pas de normalité),
- capture naturellement les **queues épaisses**, régimes de volatilité, etc., si on a assez de données.[web:153]

**Limites :**
- dépend très fortement de la **fenêtre historique** choisie (1 an vs 5 ans),
- suppose que « le futur ressemble au passé » (stationnarité), ce qui est discutable en période de crise.[web:145]

### 4.3. Application France (esquisse)

Pour TotalEnergies, CAC 40 et OAT 10 ans, on peut :
- télécharger 5 ans d’historique de prix (ou de taux pour l’OAT),
- calculer les rendements journaliers,
- calculer la VaR historique 95 % et 99 % pour un capital donné (ex : 100 k€) et comparer les 3 profils de risque.[web:148][web:152]

---

## 5. VaR paramétrique (Variance–Covariance)

### 5.1. Hypothèse normale

La **VaR paramétrique gaussienne** suppose que les rendements sont **normaux** avec moyenne \(\mu\) et écart‑type \(\sigma\).  
Pour une position monétaire \(P\) et horizon 1 jour :
- la perte journalière \(L \approx -P R\),
- \(R \sim \mathcal{N}(\mu, \sigma^2)\).

Pour un niveau de confiance \(\alpha\) :
\[ \text{VaR}_\alpha \approx P \left( z_{\alpha} \sigma - \mu \right), \]  
où \(z_\alpha\) est le quantile standard normal (par ex. \(z_{0.95} \approx 1.645\), \(z_{0.99} \approx 2.33\)).[web:153]

### 5.2. Portefeuille multi‑actifs

Pour un vecteur de poids \(w\) et un vecteur de rendements \(R\) de covariance \(\Sigma\) :
- \(\Delta P = w^T R\),
- variance du P&L : \(\sigma_P^2 = w^T \Sigma w\),
- VaR \(\alpha\) paramétrique : \(\text{VaR}_\alpha \approx z_\alpha \sigma_P - \mu_P\), avec \(\mu_P = w^T \mu\).[web:153]

### 5.3. Limites de la normalité

Les rendements d’actions et d’indices ont souvent :
- **queues épaisses** (kurtosis positive),
- asymétrie (skewness),
- volatilité conditionnelle (GARCH, clustering).[web:145]

La VaR gaussienne a tendance à **sous‑estimer les pertes extrêmes**, surtout en marché stressé, ce qui a été largement documenté dans la littérature Bâle et post‑crise 2008.[web:146][web:151]

### 5.4. Alternatives : Student‑t et modèles plus riches

Une amélioration simple : supposer les rendements **Student‑t** (qui ont des queues plus épaisses) et utiliser le quantile de cette loi pour la VaR. [web:145]  
On peut également coupler avec des modèles de volatilité conditionnelle (GARCH) pour mieux capter le clustering de volatilité dans le temps. [web:153]

---

## 6. VaR Monte Carlo

### 6.1. Idée générale

La VaR Monte Carlo consiste à **simuler de nombreux scénarios de prix futurs**, selon un modèle stochastique (par ex. GBM, Jump Diffusion), puis à calculer la distribution des P&L et en extraire le quantile. [web:145]  
Étapes :
1. Estimer les paramètres (\(\mu, \sigma, \Sigma, \) paramètres de sauts…).
2. Simuler \(N\) trajectoires de rendements sur l’horizon choisi.
3. Calculer le P&L sur chaque trajectoire.
4. Trier les P&L et prendre le quantile \(\alpha\).

### 6.2. Avantages

- grande **flexibilité** (on peut incorporer volatilité stochastique, sauts, scénarios de stress),
- permet de traiter des portefeuilles non linéaires (options) en recalculant la valeur du portefeuille dans chaque scénario.[web:145]

### 6.3. Limites

- **dépend du modèle** choisi : si le modèle est mal calibré, la VaR sera trompeuse,
- nécessite un temps de calcul plus élevé,
- peut être difficile à expliquer à un comité de risque non quant. [web:145]

---

## 7. Expected Shortfall / CVaR

### 7.1. Définition

L’**Expected Shortfall (ES)**, ou **Conditional VaR (CVaR)**, mesure la **perte moyenne au‑delà de la VaR**.  
Pour un niveau de confiance \(\alpha\) :
\[ \text{ES}_\alpha = \mathbb{E}[L \mid L \ge \text{VaR}_\alpha]. \]  
Autrement dit, si la VaR 99 % est 10 M€, l’ES 99 % peut par exemple être 15 M€ : en moyenne, **quand** on dépasse la VaR, on perd 15 M€.[web:145][web:153]

### 7.2. Pourquoi l’ES est préférée à la VaR

L’ES est **cohérente** au sens d’Artzner (sub‑additive, etc.), alors que la VaR ne l’est pas toujours. [web:145]  
Elle donne une information sur la **gravité des pertes extrêmes**, pas seulement un seuil.  
C’est pourquoi le Comité de Bâle a recommandé de passer d’une mesure basée sur la VaR (99 %, 10 jours) vers une mesure basée sur l’ES dans les exigences minimales de capital de marché.[web:151]

### 7.3. Estimation empirique

En pratique (méthode historique) :
1. on calcule la VaR \(\alpha\),
2. on identifie toutes les pertes \(L_i\) **supérieures** à la VaR,
3. l’ES est la **moyenne** de ces pertes extrêmes. [web:145]

Sur données simulées (Monte Carlo), on fait exactement la même chose sur les scénarios simulés.

---

## 8. Backtesting de la VaR (Kupiec)

### 8.1. Idée du backtesting

La VaR est un modèle. On doit le **tester** sur données historiques pour voir si la fréquence des dépassements (exceptions) est cohérente avec le niveau de confiance annoncé. [web:121]  
Par exemple, si on annonce une VaR 99 % journalière, on s’attend à environ **1 % de jours** où la perte réelle dépasse la VaR.[web:154]

### 8.2. Test de Kupiec (Proportion of Failures)

Le test de **Kupiec** (1995) teste si la **proportion observée d’exceptions** est compatible avec \(1-\alpha\). [web:124]

Notations :
- \(T\) : nombre total de jours de backtest,
- \(n_f\) : nombre de jours où la perte dépasse la VaR (exceptions),
- \(p = 1 - \alpha\) (ex : 0.01 pour 99 %).

Sous \(H_0\) (modèle correct) : \(n_f \sim \text{Binomiale}(T, p)\). [web:124]  
La statistique de log‑vraisemblance est :
\[ LR_{PoF}= -2 \log\left(\frac{(1-p)^{T-n_f}p^{n_f}}{\left(1-\frac{n_f}{T}\right)^{T-n_f}\left(\frac{n_f}{T}\right)^{n_f}}\right). \]  
Sous \(H_0\), \(LR_{PoF}\) suit approximativement une loi \(\chi^2\) à 1 ddl, donc on peut tester au niveau 95 % ou 99 %.[web:124]

Interprétation :
- si \(LR_{PoF}\) est trop grande (p‑value faible), on **rejette** le modèle de VaR : trop ou pas assez d’exceptions,
- sinon, le modèle est **acceptable** du point de vue fréquence des dépassements.[web:121]

### 8.3. Limites

- Kupiec ne teste que la **fréquence moyenne** : il ne regarde pas si les exceptions sont **regroupées** (clustering),
- d’autres tests (Christoffersen, etc.) ajoutent une dimension d’autocorrélation des exceptions.[web:121][web:154]

---

## 9. Étude France : action, indice, obligation

### 9.1. Choix du périmètre

On considère un capital de référence (par ex. 100 k€) investi séparément dans :
- TotalEnergies (`TTE.PA`) : exposition action sectorielle énergie,
- CAC 40 (`^FCHI`) : exposition marché actions France large cap,
- OAT France 10 ans : exposition taux souverain français (via rendement 10Y).[web:148][web:152]

Horizon : 1 jour, VaR 95 % et 99 %.  
Fenêtre historique : au moins 3 à 5 ans de données quotidiennes, pour une estimation robuste de la VaR historique et des paramètres paramétriques. [web:153]

### 9.2. Étapes de l’étude

Pour chaque actif :
1. récupérer les prix/taux historiques,
2. calculer les rendements journaliers (log ou simples),
3. calculer :
   - VaR historique 95 %/99 %,
   - VaR paramétrique gaussienne et éventuellement Student‑t,
   - VaR Monte Carlo (si on construit un petit modèle GBM/Student‑t),
   - ES historique 95 %/99 %,
4. réaliser un backtest de la VaR (par période rolling) et appliquer le test de Kupiec,
5. comparer l’intensité du risque entre action, indice et obligation.

### 9.3. Lecture qualitative attendue

En général (intuition) :
- l’action individuelle (TotalEnergies) devrait présenter une **VaR plus élevée** (en % du capital) que l’indice CAC 40, car elle est moins diversifiée,[web:145]
- l’indice CAC 40 présentera une VaR intermédiaire, mais reste soumis aux chocs macro (crises, krachs),
- l’OAT 10 ans devrait montrer une VaR (en rendement) plus faible, mais sensible à des épisodes de stress de dette souveraine ou de choc de taux.[web:148][web:152]

Les résultats précis dépendront des données réelles sur la période choisie.

---

## 10. Limites de la VaR

### 10.1. Manque d’information sur la queue

La VaR répond à : « quelle perte est dépassée dans \(1-\alpha\) des cas ? », mais **ne dit rien** sur la taille moyenne des pertes une fois la VaR dépassée. [web:145]  
Deux portefeuilles peuvent avoir la même VaR 99 %, mais un peut avoir des pertes maximales beaucoup plus fortes que l’autre.

### 10.2. Non‑cohérence

La VaR n’est pas toujours **sub‑additive** (VaR(A+B) peut être > VaR(A)+VaR(B)), ce qui est problématique pour des portefeuilles agrégés. [web:145]  
L’ES, lui, est une mesure de risque cohérente.

### 10.3. Sensibilité au choix de la fenêtre

La VaR historique dépend énormément de la période d’observation : une fenêtre incluant 2008 ou 2020 donnera des VaR très différentes d’une fenêtre « calme ».[web:146]  
Cela pose des questions de gouvernance sur le **choix du look‑back**.

### 10.4. Mauvaise prise en compte des changements de régime

La VaR purement historique ne « voit » que ce qui s’est déjà produit.  
Elle ne capture pas les **ruptures de régime** futures (nouvelle crise, changement de politique monétaire) sauf si on fait des scénarios de stress. [web:146]

---

## 11. Cheat Sheet VaR (résumé opérationnel)

### 11.1. Définitions rapides

- **VaR \(\alpha\)** : perte telle que \(\mathbb{P}(L \le \text{VaR}_\alpha) = \alpha\). Quantile de la distribution de perte.
- **ES \(\alpha\)** : perte moyenne conditionnelle à être au‑delà de la VaR \(\alpha\).
- **Horizon** : durée (1 jour, 10 jours, 1 mois…).
- **Niveau de confiance** : 95 %, 97.5 %, 99 %, etc.

### 11.2. Formules clés

1. **Rendements** :
   - \(R_t = (S_t - S_{t-1}) / S_{t-1}\),
   - \(r_t = \ln(S_t/S_{t-1})\).

2. **VaR historique (méthode simple)** :
   - trier les P&L historiques,
   - VaR 95 % = 5‑ème centile de la distribution (signe adapté).

3. **VaR gaussienne (1 actif)** :
   - estimer \(\mu, \sigma\) des rendements,
   - \(\text{VaR}_\alpha \approx P (z_\alpha \sigma - \mu)\).

4. **VaR gaussienne (portefeuille)** :
   - covariance \(\Sigma\), poids \(w\),
   - \(\sigma_P = \sqrt{w^T \Sigma w}\), \(\mu_P = w^T \mu\),
   - \(\text{VaR}_\alpha \approx z_\alpha \sigma_P - \mu_P\).

5. **Expected Shortfall (historique)** :
   - \(\text{ES}_\alpha = \text{moyenne des pertes } L_i \text{ telles que } L_i \ge \text{VaR}_\alpha\).

6. **Test de Kupiec (backtesting VaR)** :
   - \(T\) observations, \(n_f\) exceptions, \(p = 1-\alpha\),
   - \(LR_{PoF}= -2 \log\left(\frac{(1-p)^{T-n_f}p^{n_f}}{\left(1-\frac{n_f}{T}\right)^{T-n_f}\left(\frac{n_f}{T}\right)^{n_f}}\right)\),
   - comparer à un \(\chi^2(1)\) pour décider si on rejette le modèle. [web:124]

### 11.3. Quand utiliser quelle méthode ?

- **VaR historique** :
  - + pas d’hypothèse de loi, capte bien les queues,
  - − besoin de beaucoup de données, ne voit que le passé.

- **VaR paramétrique gaussienne** :
  - + rapide, simple, utilisable en temps réel,
  - − sous‑estime souvent les queues pour actions/indices.

- **VaR paramétrique Student‑t / GARCH** :
  - + meilleure prise en compte des queues et du clustering de volatilité,
  - − calibration plus complexe.

- **VaR Monte Carlo** :
  - + très flexible, adaptée aux portefeuilles non linéaires,
  - − dépend du modèle, coûteux en calcul.

### 11.4. Bonnes pratiques

- Toujours **spécifier horizon + niveau de confiance** (ex : « VaR 1 jour 99 % »).
- Comparer **VaR et ES** : un écart énorme indique une queue très risquée.
- Faire du **backtesting régulier** (Kupiec, Christoffersen) pour vérifier que le modèle est réaliste.
- Ne jamais utiliser la VaR seule : la compléter avec des stress tests, des scénarios extrêmes, et une analyse qualitative.

---

Ce cours peut maintenant être complété par un script `main.py` dans le dépôt GitHub **var-study-france** qui calcule et trace, pour chacun des trois actifs français, la VaR historique, paramétrique et Monte Carlo, ainsi que l’ES et les résultats de backtesting sur une période récente.
