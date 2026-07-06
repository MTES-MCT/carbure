# Selects2

Ce dossier contient les composants de selection de nouvelle generation, avec deux usages principaux :

- `filter`: composants pour les barres de filtres.
- `form`: composants pour les formulaires.

## Vue d'ensemble

- `select/`: facade `Select` avec variantes `filter` et `form`.
- `multiselect/`: facade `MultiSelect` avec variantes `filter` et `form`.
- `filter/select/`: select simple pour filtres.
- `filter/multiselect/`: multiselect pour filtres.
- `form/select/`: select simple pour formulaires.
- `form/multiselect/`: multiselect pour formulaires.
- `form/combobox/`: briques partagees de trigger pour les composants form.

## Architecture actuelle

### Facades

- `select/select.tsx` choisit la variante selon `variant`.
- `multiselect/multiselect.tsx` choisit la variante selon `variant`.

Objectif: exposer une API uniforme (`Select` / `MultiSelect`) sans imposer aux ecrans de connaitre l'arborescence interne.

### Variante filter

Les composants filter reposent sur :

- un `Button` comme trigger,
- un `Dropdown`,
- une `List` (`single` ou `multiple`).

Le comportement est optimise pour la recherche/filtres (ouverture rapide, usage compact).

### Variante form

Les composants form reposent sur :

- un trigger base sur `inputs2` (`FormPickerTrigger`),
- un `Dropdown`,
- une `List` (`single` ou `multiple`).

Le trigger est un input en lecture seule avec icone chevron, pour rester coherent avec le style des champs de formulaire (`label`, `required`, `state`, messages d'erreur/succes, etc.).

## Choix de conception (form)

Les composants `form/select` et `form/multiselect` n'utilisent plus un `<select>` natif comme coquille visuelle.

Raison:

- implementation plus simple et plus lisible,
- suppression des contournements lies aux limites du select natif (notamment en multi),
- meme base technique que les autres composants interactifs (`Dropdown` + `List`).

Important: ces composants sont pilotes en React (`value` / `onChange`) et ne ciblent pas la soumission HTML native.

## Evolution conseillee

Si besoin d'un autocomplete form riche (query, async, create), reutiliser/aligner avec `autocomplete2` plutot que de reintroduire de la logique specifique dans `Select`.
