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

export type ValidDetailsDialogProps = {
  file: DoubleCountingFileInfo
  onClose: () => void
}

export const ValidDetailsDialog = ({
  file,
  onClose,
}: ValidDetailsDialogProps) => {
  const { t } = useTranslation()

  const [focus, setFocus] = useState("sourcing_forecast")

  const saveApplication = () => {
    console.log("saveApplication")
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
          action={saveApplication}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}


export default ValidDetailsDialog
