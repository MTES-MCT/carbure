import React from "react"
import { Trans, useTranslation } from "react-i18next"

import { LotUploader } from "transactions/hooks/actions/use-upload-file"
import {
  Dialog,
  DialogButtons,
  DialogText,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"

import { Upload } from "common/components/icons"
import { Box } from "common/components"
import { Button } from "common/components/button"

import styles from "./import.module.css"
import { useMatomo } from "matomo"

type ImportWrapperProps = PromptProps<File> & {
  children: React.ReactNode
}

type ImportPromptProps = PromptProps<File> & {
  uploader: LotUploader
}

const ImportWrapper = ({ children, onResolve }: ImportWrapperProps) => {
  const matomo = useMatomo()
  const { t } = useTranslation()

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={t("Import Excel")} />
      <DialogText text={t("Importer un fichier Excel standardisé.")} />

      <Box className={styles.importPrompt}>
        {children}

        <DialogButtons>
          <Button as="label" level="primary" icon={Upload}>
            <Trans>Importer lots</Trans>
            <input
              type="file"
              className={styles.importFileInput}
              onChange={(e) => {
                matomo.push(["trackEvent", "transactions", "import-batches"])
                onResolve(e!.target.files![0])
              }}
            />
          </Button>
          <Button onClick={() => onResolve()}>
            <Trans>Annuler</Trans>
          </Button>
        </DialogButtons>
      </Box>
    </Dialog>
  )
}

export const ProducerImportPrompt = ({
  uploader,
  onResolve,
}: ImportPromptProps) => (
  <ImportWrapper onResolve={onResolve}>
    <Box className={styles.importExplanation}>
      <span className={styles.note}>
        <Trans>
          Note: Le modèle a été mis à jour le 24/03/2021. La colonne
          production_site_reference n'est plus obligatoire. Votre certificat de
          fournisseur doit désormais figurer dans la colonne
          'vendor_certificate'. Veuillez vous référer au guide pour plus
          d'informations.
        </Trans>
      </span>
      <Trans>
        Le modèle simplifié vous permet de créer des lots provenant de vos
        propres usines. Vous pouvez les affilier immédiatement à des clients
        enregistrés sur Carbure ou simplement les ajouter à votre Stock.
      </Trans>
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateSimple}
      >
        Télécharger le modèle simplifié
      </span>
      <a
        className={styles.downloadLink}
        href="https://carbure-1.gitbook.io/faq/gerer-mes-lots-1/producteur-trader-ajouter-des-lots/ajout-de-lot-via-fichier-excel/modele-simplifie"
      >
        <Trans>Guide du modèle simplifié</Trans>
      </a>
    </Box>

    <Box className={styles.importExplanation}>
      <Trans>
        Le modèle avancé permet d'importer dans Carbure des lots achetés auprès
        de fournisseurs qui nous sont inconnus (fournisseurs étrangers ou
        producteurs français captifs). Vous avez également la possibilité
        d'attribuer ces lots à des clients étrangers.
      </Trans>
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateAdvanced}
      >
        <Trans>Télécharger le modèle avancé</Trans>
      </span>
      <a
        className={styles.downloadLink}
        href="https://carbure-1.gitbook.io/faq/gerer-mes-lots-1/producteur-trader-ajouter-des-lots/ajout-de-lot-via-fichier-excel/modele-complexe"
      >
        <Trans>Guide du modèle avancé</Trans>
      </a>
    </Box>
  </ImportWrapper>
)

export const OperatorImportPrompt = ({
  uploader,
  onResolve,
}: ImportPromptProps) => (
  <ImportWrapper onResolve={onResolve}>
    <Box className={styles.importExplanation}>
      <Trans>
        Le modèle Excel vous permet d'importer des lots provenant de
        fournisseurs qui ne sont pas inscrits sur Carbure. Il peut s'agir de
        lots importés depuis l'étranger ou de producteurs captifs.
      </Trans>
      <span className={styles.note}>
        <Trans>
          Note: Le modèle a été mis à jour le 24/03/2021. La colonne
          production_site_reference n'est plus obligatoire. Le certificat de
          votre fournisseur doit désormais figurer dans la colonne
          'supplier_certificate' Veuillez vous référer au guide pour plus
          d'informations.
        </Trans>
      </span>
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateOperator}
      >
        <Trans>Télécharger le modèle</Trans>
      </span>
      <a
        className={styles.downloadLink}
        href="https://carbure-1.gitbook.io/faq/gerer-mes-lots-1/operateur-petrolier/ajouter-des-lots/importer-un-fichier-excel"
      >
        <Trans>Guide de l'import Excel</Trans>
      </a>
    </Box>
  </ImportWrapper>
)

export const TraderImportPrompt = ({
  uploader,
  onResolve,
}: ImportPromptProps) => (
  <ImportWrapper onResolve={onResolve}>
    <Box className={styles.importExplanation}>
      <Trans>
        Le modèle Excel permet d'importer dans Carbure des lots achetés auprès
        de fournisseurs qui nous sont inconnus (fournisseurs étrangers ou
        producteurs français captifs). Vous avez également la possibilité
        d'attribuer ces lots à des clients étrangers.
      </Trans>
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateTrader}
      >
        <Trans>Télécharger le modèle</Trans>
      </span>
    </Box>
  </ImportWrapper>
)

export const StockImportPrompt = ({
  uploader,
  onResolve,
}: ImportPromptProps) => (
  <ImportWrapper onResolve={onResolve}>
    <Box className={styles.importExplanation}>
      <Trans>
        Ce modèle vous permet de créer des lots à partir de votre stock
      </Trans>
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateMassBalanceCarbureID}
      >
        <Trans>Télécharger le modèle 1</Trans>
      </span>
      <span
        className={styles.downloadLink}
        onClick={uploader.downloadTemplateMassBalanceBCGHG}
      >
        <Trans>Télécharger le modèle 2</Trans>
      </span>
    </Box>
  </ImportWrapper>
)
