import React, { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common-v2/hooks/async"
import { useNotify } from "common-v2/components/notifications"
import Button, { ExternalLink as Ext } from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import { Check, Return, Upload } from "common-v2/components/icons"
import { usePortal } from "common-v2/components/portal"
import { FileArea, FileInput } from "common-v2/components/input"
import { LoaderOverlay } from "common-v2/components/scaffold"
import { useMatomo } from "matomo"

const FAQ_URL = "https://carbure-1.gitbook.io/faq/"
const TEMPLATE_URL = "/api/download-template"

export const ImportButton = () => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      icon={Upload}
      label={t("Importer des lots")}
      action={() => portal((close) => <ImportDialog onClose={close} />)}
    />
  )
}

export const ImportArea = ({ children }: { children: React.ReactNode }) => {
  const { t } = useTranslation()
  const matomo = useMatomo()
  const entity = useEntity()
  const importLots = useImportLots()

  return (
    <FileArea
      icon={Upload}
      label={t("Importer le fichier\nsur la plateforme")}
      onChange={(file) => {
        matomo.push(["trackEvent", "lots-create", "drag-and-drop-lots-excel"])
        importLots.execute(entity.id, file!)
      }}
    >
      {children}
      {importLots.loading && <LoaderOverlay />}
    </FileArea>
  )
}

interface ImportDialogProps {
  onClose: () => void
}

const ImportDialog = ({ onClose }: ImportDialogProps) => {
  const { t } = useTranslation()
  const matomo = useMatomo()
  const entity = useEntity()

  const importLots = useImportLots(onClose)

  const [file, setFile] = useState<File | undefined>()

  return (
    <Dialog limit onClose={onClose}>
      <header>
        <h1>{t("Import Excel")}</h1>
      </header>
      <main>
        <section>
          <p>
            <Trans>
              Vous pouvez importer plusieurs lots à la fois en important un
              fichier excel à travers le champ au bas de cette fenêtre.
            </Trans>
          </p>
          <p>
            <Trans>
              Notez que vous pouvez aussi réaliser un <i>drag-and-drop</i> de
              votre fichier Excel directement sur la page Transactions de
              CarbuRe afin d'accélérer cette procédure.
            </Trans>
          </p>
        </section>
        <section>
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

function useImportLots(onClose?: () => void) {
  const { t } = useTranslation()
  const notify = useNotify()

  return useMutation(api.importLots, {
    invalidates: ["lots", "snapshot", "lot-summary"],

    onSuccess: () => {
      notify(t("Les lots ont bien été importés"), { variant: "success" })
      onClose?.()
    },

    onError: () => {
      notify(t("Les lots n'ont pas pu être importés"), { variant: "danger" })
      onClose?.()
    },
  })
}
