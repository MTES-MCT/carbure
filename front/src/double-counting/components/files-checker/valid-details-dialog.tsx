import { findProducers, findProductionSites } from "carbure/api"
import useEntity from "carbure/hooks/entity"
import { Entity, ProductionSite } from "carbure/types"
import * as norm from "carbure/utils/normalizers"
import Autocomplete from "common/components/autocomplete"
import { Button, ExternalLink, MailTo } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { useForm } from "common/components/form"
import { AlertTriangle, Plus, Return } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import Tabs from "common/components/tabs"
import Tag from "common/components/tag"
import { useMutation } from "common/hooks/async"
import { addDoubleCountingApplication } from "double-counting/api"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useMatch } from "react-router-dom"
import { DoubleCountingFileInfo } from "../../types"
import ApplicationInfo from "../application/application-info"
import { ProductionTable, SourcingFullTable } from "../dc-tables"
import Alert from "common/components/alert"

export type ValidDetailsDialogProps = {
  file: File
  fileData: DoubleCountingFileInfo
  onClose: () => void
}

export const ValidDetailsDialog = ({
  file,
  fileData,
  onClose,
}: ValidDetailsDialogProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const isProducerMatch = useMatch("/org/:entity/settings*")
  const [focus, setFocus] = useState("sourcing_forecast")

  function showProductionSiteDialog() {
    if (isProducerMatch) {
      portal((close) => <MailToDialog onClose={() => { close(); onClose() }} fileData={fileData} />)
    } else {
      portal((close) => <ProductionSiteAdminDialog fileData={fileData} onClose={() => { close(); onClose() }} file={file} />)
    }
  }

  return (
    <Dialog fullscreen onClose={onClose}>
      <header>
        <Tag big variant="success">
          {t("Valide")}
        </Tag>
        <h1>{t("Ajout du dossier double comptage")}</h1>
      </header>

      <main>

        <ApplicationInfo fileData={fileData} />
        <section>
          {fileData.has_dechets_industriels &&
            <DechetIndustrielAlert />
          }
        </section>
        <section>
          <Tabs
            variant="switcher"
            tabs={[
              {
                key: "sourcing_forecast",
                label: t("Approvisionnement"),
              },
              {
                key: "production",
                label: t("Production"),
              }

            ]}
            focus={focus}
            onFocus={setFocus}
          />

        </section>

        {focus === "sourcing_forecast" &&
          <section>
            <SourcingFullTable
              sourcing={fileData.sourcing ?? []}
            />
          </section>
        }


        {focus === "production" &&
          <section>
            <ProductionTable
              production={fileData.production ?? []}
            />
          </section>
        }
      </main>

      <footer>
        <Button
          icon={Plus}
          label={isProducerMatch ? t("Envoyer le dossier") : t("Ajouter le dossier")}
          variant="primary"
          action={showProductionSiteDialog}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}
const defaultProductionForm = {
  productionSite: undefined as ProductionSite | undefined,
  producer: undefined as Entity | undefined,
}

type ProductionForm = typeof defaultProductionForm

export type ProductionSiteDialogProps = {
  file: File
  fileData: DoubleCountingFileInfo
  onClose: () => void
}

export const ProductionSiteAdminDialog = ({
  file,
  fileData,
  onClose,
}: ProductionSiteDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const { value, bind } =
    useForm<ProductionForm>(defaultProductionForm)
  const notify = useNotify()


  const addApplication = useMutation(addDoubleCountingApplication, {
    invalidates: [],
  })

  const saveApplication = async () => {
    if (!value.productionSite || !value.producer) return
    try {
      await addApplication.execute(
        entity.id,
        value.productionSite.id,
        value.producer.id,
        file
      )
      onClose()
      notify(t("Dossier ajouté avec succès"), { variant: "success" })
    } catch (err) {
      notify(t("Impossible d'ajouter le dossier"), { variant: "warning" })
    }
  }
  const producer = value.producer instanceof Object ? value.producer.id : undefined // prettier-ignore


  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Ajout du dossier double comptage")}</h1>
      </header>

      <main>
        <ApplicationInfo fileData={fileData} />
        <section>
          <Autocomplete
            required
            label={t("Producteur")}
            getOptions={findProducers}
            normalize={norm.normalizeEntity}
            {...bind("producer")}
          />
          <Autocomplete
            required
            label={t("Site de production")}
            getOptions={(query) => findProductionSites(query, producer)}
            normalize={norm.normalizeProductionSite}
            {...bind("productionSite")}
          />
        </section>
      </main>

      <footer>
        <Button
          icon={Plus}
          label={t("Ajouter le dossier")}
          variant="primary"
          disabled={addApplication.loading || !value.productionSite || !value.producer}
          action={saveApplication}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}


const DechetIndustrielAlert = () => {
  return <Alert variant="warning" icon={AlertTriangle}>
    <Trans>
      Spécifité "Déchets industriels" : Une demande concernant des déchets industriels doit être accompagnée du questionnaire de processus de validation pour ces matières premieres{" "}
      {/* <a href="./templates/test.docx" target="_blank" rel="noopener noreferrer">disponible ici</a>. */}
      <ExternalLink href={"https://www.ecologie.gouv.fr/sites/default/files/Processus%20de%20validation%20de%20mati%C3%A8res%20premi%C3%A8res.pdf"}>
        disponible ici
      </ExternalLink>
      . Merci de le joindre à votre demande par email.
    </Trans>
  </Alert>
}

export const MailToDialog = ({
  onClose,
  fileData,
}: { onClose: () => void, fileData: DoubleCountingFileInfo }) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const dechetsIndustrielMessage = fileData.has_dechets_industriels ? "%0D%0A-%20le%20questionnaire%20de%20processus%20de%20validation%20des%20mati%C3%A8res%20premieres%20rempli%20pour%20les%20d%C3%A9chets%20industriels%20mentionn%C3%A9s" : ""
  const bodyMessage = `Mesdames%2C%20Messieurs%2C%0D%0A%0D%0AJe%20vous%20faire%20parvenir%20le%20dossier%20de%20demande%20de%20reconnaissance%20au%20Double%20Comptage%20pour%20notre%20soci%C3%A9t%C3%A9.%0D%0AJ'ai%20joint%20%20%3A%0D%0A-%20le%20fichier%20Excel%20apr%C3%A8s%20validation%20avec%20la%20plateforme%20CarbuRe${dechetsIndustrielMessage}%0D%0A%0D%0ABien%20cordialement`

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Envoi du dossier double comptage")}</h1>
      </header>

      <main>
        <section>
          <p style={{ textAlign: 'left' }}>
            {t("Votre fichier est valide. Vous pouvez le transmettre par email à la DGEC pour une vérification approfondie à l'adresse carbure@beta.gouv.fr en cliquant ci-dessous : ")}
          </p>
          {fileData.has_dechets_industriels &&
            <DechetIndustrielAlert />
          }
          <MailTo user="carbure" host="beta.gouv.fr"
            subject={`[CarbuRe - Double comptage] Demande de ${entity.name}`}
            body={bodyMessage}
          >
            <Trans>Envoyer la demande par email</Trans>
          </MailTo>

        </section>
      </main>

      <footer>
        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}



export default ValidDetailsDialog


