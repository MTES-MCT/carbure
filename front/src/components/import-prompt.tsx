import React from "react"

import { LotUploader } from "../hooks/actions/use-upload-file"
import { PromptFormProps } from "./system/dialog"

import styles from "./import-prompt.module.css"

import { Upload } from "./system/icons"
import { Box, Button } from "./system"

const ImportPrompt = ({
  children,
  onConfirm,
  onCancel,
}: PromptFormProps<File>) => (
  <Box className={styles.importPrompt}>
    {children}

    <Box row className={styles.dialogButtons}>
      <Button as="label" level="primary" icon={Upload}>
        Importer lots
        <input
          type="file"
          className={styles.importFileInput}
          onChange={(e) => onConfirm(e!.target.files![0])}
        />
      </Button>
      <Button onClick={onCancel}>Annuler</Button>
    </Box>
  </Box>
)

export const ProducerImportPromptFactory = (uploader: LotUploader) => ({
  onConfirm,
  onCancel,
}: PromptFormProps<File>) => (
  <ImportPrompt onConfirm={onConfirm} onCancel={onCancel}>
    <Box className={styles.importExplanation}>
      Le modèle simplifié vous permet de créer des lots provenant de vos propres
      usines. Vous pouvez les affilier immédiatement à des clients enregistrés
      sur Carbure ou simplement les ajouter à votre Mass Balance.
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateSimple}
      >
        Télécharger le modèle simplifié
      </span>
    </Box>

    <Box className={styles.importExplanation}>
      Le modèle avancé permet d'importer dans Carbure des lots achetés auprès de
      fournisseurs qui nous sont inconnus (fournisseurs étrangers ou producteurs
      français captifs). Vous avez également la possibilité d'attribuer ces lots
      à des clients étrangers.
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateAdvanced}
      >
        Télécharger le modèle avancé
      </span>
    </Box>
  </ImportPrompt>
)

export const OperatorImportPromptFactory = (uploader: LotUploader) => ({
  onConfirm,
  onCancel,
}: PromptFormProps<File>) => (
  <ImportPrompt onConfirm={onConfirm} onCancel={onCancel}>
    <Box className={styles.importExplanation}>
      Le modèle Excel vous permet d'importer des lots provenant de fournisseurs
      qui ne sont pas inscrits sur Carbure. Il peut s'agir de lots importés
      depuis l'étranger ou de producteurs captifs.
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateOperator}
      >
        Télécharger le modèle
      </span>
    </Box>
  </ImportPrompt>
)

export const StockImportPromptFactory = (uploader: LotUploader) => ({
  onConfirm,
  onCancel,
}: PromptFormProps<File>) => (
  <ImportPrompt onConfirm={onConfirm} onCancel={onCancel}>
    <Box className={styles.importExplanation}>
      Ce modèle vous permet de créer des lots à partir de votre Mass Balance
      (onglet Lots en Stock)
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateMassBalance}
      >
        Télécharger le modèle
      </span>
    </Box>
  </ImportPrompt>
)
