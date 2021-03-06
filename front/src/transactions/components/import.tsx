import React from "react"

import { LotUploader } from "transactions/hooks/actions/use-upload-file"
import { DialogButtons, PromptFormProps } from "common/components/dialog"

import { Upload } from "common/components/icons"
import { Box } from "common/components"
import { Button } from "common/components/button"

import styles from "./import.module.css"

const ImportPrompt = ({
  children,
  onConfirm,
  onCancel,
}: PromptFormProps<File>) => (
  <Box className={styles.importPrompt}>
    {children}

    <DialogButtons>
      <Button as="label" level="primary" icon={Upload}>
        Importer lots
        <input
          type="file"
          className={styles.importFileInput}
          onChange={(e) => onConfirm(e!.target.files![0])}
        />
      </Button>
      <Button onClick={onCancel}>Annuler</Button>
    </DialogButtons>
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
      sur Carbure ou simplement les ajouter à votre Stock.
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

export const TraderImportPromptFactory = (uploader: LotUploader) => ({
  onConfirm,
  onCancel,
}: PromptFormProps<File>) => (
  <ImportPrompt onConfirm={onConfirm} onCancel={onCancel}>
    <Box className={styles.importExplanation}>
      Le modèle Excel permet d'importer dans Carbure des lots achetés auprès de
      fournisseurs qui nous sont inconnus (fournisseurs étrangers ou producteurs
      français captifs). Vous avez également la possibilité d'attribuer ces lots
      à des clients étrangers.
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateTrader}
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
      Ce modèle vous permet de créer des lots à partir de votre stock
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateMassBalanceCarbureID}
      >
        Télécharger le modèle 1
      </span>
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateMassBalanceBCGHG}
      >
        Télécharger le modèle 2
      </span>
    </Box>
  </ImportPrompt>
)
