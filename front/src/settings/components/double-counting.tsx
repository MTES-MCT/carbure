import { Trans, useTranslation } from "react-i18next"

import { EntitySelection } from "carbure/hooks/use-entity"
import { CompanySettingsHook as DoubleContingSettingsHook } from "../hooks/use-company"
import { ProductionSite, UserRole } from "common/types"
import { Title, LoaderOverlay } from "common/components"
import { SectionHeader, SectionBody, Section } from "common/components/section"
import { useRights } from "carbure/hooks/use-rights"
import Table from "common/components/table"
import styles from "./settings.module.css"
import { Button } from "common/components/button"
import {
  AlertCircle,
  Check,
  Plus,
  Return,
  Save,
  Upload,
} from "common/components/icons"
import { Alert } from "common/components/alert"
import {
  Dialog,
  DialogButtons,
  DialogTitle,
  prompt,
  PromptProps,
} from "common/components/dialog"
import { SettingsForm } from "./common"
import { useState } from "react"
import { findProductionSites } from "common/api"
import { LabelAutoComplete } from "common/components/autocomplete"

type DoubleCountingUploadPromptProps = PromptProps<void> & {
  entity: EntitySelection
}

const DoubleCountingUploadPrompt = ({
  entity,
  onResolve,
}: DoubleCountingUploadPromptProps) => {
  const { t } = useTranslation()

  const [productionSite, setProductionSite] = useState<ProductionSite | null>(
    null
  )

  const [sourcingFile, setSourcingFile] = useState<File | null>(null)
  const [productionFile, setProductionFile] = useState<File | null>(null)

  return (
    <Dialog onResolve={onResolve} className={styles.settingsPrompt}>
      <DialogTitle text={t("Création dossier double comptage")} />

      <SettingsForm>
        <div className={styles.settingsText}>
          <Trans>
            Commencez dans un premier temps par renseigner le site de production
            concerné par votre demande.
          </Trans>
        </div>

        <LabelAutoComplete
          label={t("Site de production")}
          placeholder={t("Rechercher un site de production")}
          className={styles.settingsField}
          value={productionSite}
          onChange={(e: any) => setProductionSite(e.target.value)}
          getQuery={findProductionSites}
          getValue={(ps: any) => ps.id}
          getLabel={(ps: any) => ps.name}
          queryArgs={[entity?.id]}
          minLength={0}
        />

        <div className={styles.settingsText}>
          <a
            href="/api/v3/double-count/get-template?file_type=SOURCING"
            className={styles.settingsLink}
          >
            <Trans>Téléchargez le modèle suivant</Trans>
          </a>
          <Trans>
            {" "}
            afin de renseigner les différentes sources d'approvisionnement en
            matières premières sujettes au double comptage.
          </Trans>
        </div>

        <Button
          as="label"
          level={sourcingFile ? "success" : "primary"}
          icon={sourcingFile ? Check : Upload}
          className={styles.settingsFormButton}
        >
          {sourcingFile ? (
            sourcingFile.name
          ) : (
            <Trans>Importer les informations d'approvisionnement</Trans>
          )}
          <input
            type="file"
            className={styles.importFileInput}
            onChange={(e) => setSourcingFile(e!.target.files![0])}
          />
        </Button>

        <div className={styles.settingsText}>
          <a
            href="/api/v3/double-count/get-template?file_type=PRODUCTION"
            className={styles.settingsLink}
          >
            <Trans>Télécharger le modèle pour la production</Trans>
          </a>
          <Trans>
            {" "}
            pour lister la partie de votre production basée sur les matières
            premières sujettes au double comptage.
          </Trans>
        </div>

        <Button
          as="label"
          level={productionFile ? "success" : "primary"}
          icon={productionFile ? Check : Upload}
          className={styles.settingsFormButton}
        >
          {productionFile ? (
            productionFile.name
          ) : (
            <Trans>Importer les objectifs de production</Trans>
          )}
          <input
            type="file"
            className={styles.importFileInput}
            onChange={(e) => setProductionFile(e!.target.files![0])}
          />
        </Button>

        <DialogButtons>
          <Button level="primary" icon={Check} onClick={() => onResolve()}>
            <Trans>Valider</Trans>
          </Button>
          <Button icon={Return} onClick={() => onResolve()}>
            <Trans>Annuler</Trans>
          </Button>
        </DialogButtons>
      </SettingsForm>
    </Dialog>
  )
}

type DoubleCountingSettingsProps = {
  entity: EntitySelection
  settings: DoubleContingSettingsHook
}

const DoubleCountingSettings = ({
  entity,
  settings,
}: DoubleCountingSettingsProps) => {
  const { t } = useTranslation()
  const rights = useRights()

  const isEmpty = true
  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

  const columns: any[] = []
  const rows: any[] = []

  return (
    <Section id="double-counting">
      <SectionHeader>
        <Title>
          <Trans>Dossiers double comptage</Trans>
        </Title>
        {canModify && (
          <Button
            level="primary"
            icon={Plus}
            onClick={() =>
              prompt((resolve) => (
                <DoubleCountingUploadPrompt
                  entity={entity}
                  onResolve={resolve}
                />
              ))
            }
          >
            <Trans>Ajouter un dossier double comptage</Trans>
          </Button>
        )}
      </SectionHeader>

      {isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            <Trans>Aucun dossier double comptage trouvé</Trans>
          </Alert>
        </SectionBody>
      )}

      {!isEmpty && (
        <Table columns={columns} rows={rows} className={styles.settingsTable} />
      )}

      {settings.isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default DoubleCountingSettings
