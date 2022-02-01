import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common-v2/hooks/async"
import { useNotify } from "common-v2/components/notifications"
import Button, { ExternalLink as Ext } from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import { Check, Return, Upload } from "common-v2/components/icons"
import { usePortal } from "common-v2/components/portal"
import { FileInput } from "common-v2/components/input"
import { useMatomo } from "matomo"

const FAQ_URL = "https://carbure-1.gitbook.io/faq/gerer-mes-lots-1/producteur-trader-ajouter-des-lots/ajout-de-lot-via-fichier-excel" // prettier-ignore
const TEMPLATE_URL = "/api/download-template-stock"

export const StockExcelButton = () => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      icon={Upload}
      label={t("Extraire avec excel")}
      action={() => portal((close) => <StockExcelDialog onClose={close} />)}
    />
  )
}

interface StockExcelDialogProps {
  onClose: () => void
}

const StockExcelDialog = ({ onClose }: StockExcelDialogProps) => {
  const { t } = useTranslation()
  const matomo = useMatomo()
  const entity = useEntity()

  const importLots = useExtractStock(onClose)

  const [file, setFile] = useState<File | undefined>()

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Extraire des lots des stocks avec Excel")}</h1>
      </header>
      <main>
        <section>
          <p>
            <Trans>
              En important un fichier excel à travers le champ au bas de cette
              fenêtre, vous pourrez créer plusieurs lots basés sur vos stocks
              listés sur CarbuRe.
            </Trans>
          </p>
          <p>
            <Trans>
              Notez que vous pouvez aussi réaliser un drag-and-drop de votre
              fichier Excel directement sur la page Transactions de CarbuRe afin
              d'accélérer cette procédure.
            </Trans>
          </p>
          <p>
            <Trans>
              Ce fichier doit respecter certaines règles dont vous trouverez les
              détails dans <Ext href={FAQ_URL}>notre FAQ</Ext>.
            </Trans>
          </p>
          <p>
            <Trans>
              Avant de commencer, veillez à télécharger le modèle disponible{" "}
              <Ext href={TEMPLATE_URL + `?entity_id=${entity.id}`}>
                sur ce lien
              </Ext>
              .
            </Trans>
          </p>
          {/* <p>
            <Trans>
              Son contenu dépend des filtres ou de la sélection que vous avez
              appliqué à la page Stock avant d'ouvrir cette fenêtre : pour
              chaque stock trouvé, vous trouverez une ligne préremplie dans le
              fichier.
            </Trans>
          </p> */}
        </section>
        <section>
          <FileInput
            loading={importLots.loading}
            icon={file ? Check : Upload}
            label={t("Fichier excel")}
            placeholder={file ? file.name : t("Importer un fichier")}
            onChange={setFile}
          />
        </section>
      </main>
      <footer>
        <Button
          asideX
          disabled={importLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
        <Button
          loading={importLots.loading}
          disabled={!file}
          variant="primary"
          icon={Upload}
          label={t("Importer")}
          action={() => {
            matomo.push(["trackEvent", "lots-create", "import-lots-excel"])
            importLots.execute(entity.id, file!)
          }}
        />
      </footer>
    </Dialog>
  )
}

function useExtractStock(onClose?: () => void) {
  const { t } = useTranslation()
  const notify = useNotify()

  return useMutation(api.importLots, {
    invalidates: ["lots", "snapshot", "lot-summary"],

    onSuccess: () => {
      notify(
        t("Les lots extraits des stocks ont bien été ajoutés à vos brouillons !"), // prettier-ignore
        { variant: "success" }
      )
      onClose?.()
    },

    onError: () => {
      notify(t("L'extraction des stocks a échoué"), { variant: "danger" })
      onClose?.()
    },
  })
}
