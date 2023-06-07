import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Plus, Return } from "common/components/icons"
import Tabs from "common/components/tabs"
import Tag from "common/components/tag"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { DoubleCountingFileInfo } from "../../types"
import ApplicationInfo from "../application/application-info"
import { ProductionTable, SourcingFullTable } from "../dc-tables"
import { usePortal } from "common/components/portal"
import Autocomplete from "common/components/autocomplete"
import { ProductionSiteField } from "lot-add/components/production-fields"
import { findProductionSites } from "carbure/api"

export type ValidDetailsDialogProps = {
  file: DoubleCountingFileInfo
  onClose: () => void
}

export const ValidDetailsDialog = ({
  file,
  onClose,
}: ValidDetailsDialogProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const [focus, setFocus] = useState("sourcing_forecast")


  function showProductionSiteDialog() {
    portal((close) => <ProductionSiteDialog file={file} onClose={close} />)
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

        <ApplicationInfo file={file} />
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
              sourcing={file.sourcing ?? []}
            />
          </section>
        }


        {focus === "production" &&
          <section>
            <ProductionTable
              production={file.production ?? []}
            />
          </section>
        }
      </main>

      <footer>
        <Button
          icon={Plus}
          label={t("Ajouter le dossier")}
          variant="primary"
          action={showProductionSiteDialog}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}


export const ProductionSiteDialog = ({
  file,
  onClose,
}: ValidDetailsDialogProps) => {
  const { t } = useTranslation()

  const saveApplication = () => {
    console.log("saveApplication")
  }


  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Ajout du dossier double comptage")}</h1>
      </header>

      <main>

        <ApplicationInfo file={file} />

        {/* Choix du producteur  */}
        {/* 
        Choix du site de production
        <Autocomplete
      required
      label={t("Site de production")}
      value={productionSite}
      icon={isKnown ? UserCheck : undefined}
      defaultOptions={isKnown ? [productionSite] : undefined}
      getOptions={(query) => findProductionSites(query, producer)}
      normalize={norm.normalizeProductionSiteOrUnknown}
      {...bound}
      {...props}
    /> */}

      </main>

      <footer>
        <Button
          icon={Plus}
          label={t("Ajouter le dossier")}
          variant="primary"
          action={saveApplication}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}

export default ValidDetailsDialog


