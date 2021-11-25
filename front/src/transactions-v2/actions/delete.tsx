import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Lot, LotQuery } from "../types"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common-v2/hooks/async"
import { useNotify } from "common-v2/components/notifications"
import { variations } from "common-v2/utils/formatters"
import Button from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import { Cross, Return } from "common-v2/components/icons"
import { usePortal } from "common-v2/components/portal"
import { LotSummary } from "../components/lots/lot-summary"

export interface DeleteButtonProps {
  disabled?: boolean
  query: LotQuery
  selection: number[]
}

export const DeleteManyButton = ({
  disabled,
  query,
  selection,
}: DeleteButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled}
      variant="danger"
      icon={Cross}
      label={
        selection.length > 0 ? t("Supprimer la sélection") : t("Supprimer tout")
      }
      action={() =>
        portal((close) => (
          <DeleteDialog
            summary
            query={query}
            selection={selection}
            onClose={close}
          />
        ))
      }
    />
  )
}

export interface DeleteIconButtonProps {
  icon?: boolean
  lot: Lot
}

export const DeleteOneButton = ({ icon, lot }: DeleteIconButtonProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "danger"}
      icon={Cross}
      title={t("Supprimer le lot")}
      label={t("Supprimer le lot")}
      action={() =>
        portal((close) => (
          <DeleteDialog
            query={{ entity_id: entity.id }}
            selection={[lot.id]}
            onClose={close}
          />
        ))
      }
    />
  )
}

interface DeleteDialogProps {
  summary?: boolean
  query: LotQuery
  selection: number[]
  onClose: () => void
}

const DeleteDialog = ({
  summary,
  query,
  selection,
  onClose,
}: DeleteDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()

  const v = variations(selection.length)

  const deleteLots = useMutation(api.deleteLots, {
    invalidates: ["lots", "snapshot"],

    onSuccess: () => {
      const text = v({
        zero: t("Les lots ont bien été supprimés !"),
        one: t("Le lot a bien été supprimé !"),
        many: t("Les lots sélectionnés ont bien été supprimés !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        zero: t("Les lots n'ont pas pu être supprimés !"),
        one: t("Le lot n'a pas pu être supprimé !"),
        many: t("Les lots sélectionnés n'ont pas pu être supprimés !"),
      })

      notify(text, { variant: "danger" })
      onClose()
    },
  })

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>
          {v({
            zero: t("Supprimer tous les lots"),
            one: t("Supprimer ce lot"),
            many: t("Supprimer les lots sélectionnés"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            zero: t("Voulez-vous supprimer ces lots ?"),
            one: t("Voulez-vous supprimer ce lot ?"),
            many: t("Voulez-vous supprimer les lots sélectionnés ?"),
          })}
        </section>
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          disabled={deleteLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
        <Button
          submit
          loading={deleteLots.loading}
          variant="danger"
          icon={Cross}
          label={t("Supprimer")}
          action={() => deleteLots.execute(query, selection)}
        />
      </footer>
    </Dialog>
  )
}
