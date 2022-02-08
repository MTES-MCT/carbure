# Evenements utilisateur envoyés à Matomo

### Syntaxe:
- `[catégorie de l'evenement]`:
  - `[nom de l'action]` : [description]
  - `[nom de l'action] ( [information supplementaire] )` : [description]

### Evenements généraux sur la page Transaction
- `lots`:
  - `delete-lot (nombre de lots)` : suppression d'un lot
  - `send-lot (nombre de lots)` : envoi d'un brouillon
  - `export-lots-excel (nombre de lots)` : export des résultats de recherche vers excel

### Evenements généraux sur l'onglet Stock de la page Transaction
- `stocks`:
  - `split-stock` : extraire un lot depuis un stock
  - `export-stocks-excel (nombre de lots)` : créer des lots depuis les stocks avec excel

### Evenements relatifs à la création de lot
- `lots-create`:
  - `create-lot-with-form` : création d'un lot en utilisant le formulaire
  - `drag-and-drop-lots-excel` : import de lots en drag-and-droppant un fichier excel
  - `import-lots-excel` : import de lots en utilisant le menu d'importation

### Evenements relatifs aux détails d'un lot existant
- `lots-details`:
  - `show-lot-details (id du lot)` : afficher un lot
  - `save-lot-changes` : sauvegarder les modifications sur un lot

### Evenements relatifs aux différents types d'acceptation de lots
- `lots-accept`:
  - `release-for-consumption (nombre de lots)` : mise à consommation
  - `to-stock (nombre de lots)` : mise en stock
  - `blending (nombre de lots)` : incorporation
  - `direct-delivery (nombre de lots)` : livraison directe
  - `exportation (nombre de lots)` : exportation
  - `transfer-without-stock (nombre de lots)` : transfert de lot
  - `processing (nombre de lots)` : processing du lot par un opérateur tiers

### Evenements relatifs aux corrections
- `lot-corrections`:
  - `client-reject-lot (nombre de lots)` : le client du lot refuse le lot reçu
  - `client-request-fix (nombre de lots)` : le client demande une correction
  - `supplier-recall-lot (nombre de lots)` : le fournisseur du lot rappelle le lot pour le corriger
  - `supplier-mark-as-fixed (nombre de lots)` : le fournisseur confirme que la correction est terminée
  - `client-approve-fix (nombre de lots)` : le client accepte la correction

### Evenements relatifs aux déclarations
- `declarations`:
  - `validate-declaration (periode de declaration)` : valider une déclaration
  - `invalidate-declaration (periode de declaration)` : annuler une déclaration

### Evenements relatifs à la gestion du compte utilisateur
- `account`:
  - `add-access-right` : ajouter un accès à une entité

### Evenements relatifs au contexte de la page
- `menu`:
  - `change-language (langue)` : changer la langue de l'application
  - `change-entity (entité)` : changer l'entité sélectionnée