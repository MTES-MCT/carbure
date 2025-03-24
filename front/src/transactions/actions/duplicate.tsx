import { useTranslation } from "react-i18next"
import { Lot, LotQuery } from "../types"
import * as api from "../api"
import useEntity from "common/hooks/entity"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { variations } from "common/utils/formatters"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Copy, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LotSummary } from "../components/lots/lot-summary"
import { useMatomo } from "matomo"

export interface DuplicateOneButtonProps {
  icon?: boolean
  lot: Lot
}

export const DuplicateOneButton = ({ icon, lot }: DuplicateOneButtonProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "primary"}
      icon={Copy}
      title={t("Dupliquer")}
      label={t("Dupliquer")}
      action={() =>
        portal((close) => (
          <DuplicateDialog
            query={{ entity_id: entity.id }}
            selection={[lot.id]}
            onClose={close}
          />
        ))
      }
    />
  )
}

interface DuplicateDialogProps {
  summary?: boolean
  query: LotQuery
  selection: number[]
  onClose: () => void
}

const DuplicateDialog = ({
  summary,
  query,
  selection,
  onClose,
}: DuplicateDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()
  const entity = useEntity()

  const v = variations(selection.length)

  const duplicateLots = useMutation(api.duplicateLots, {
    invalidates: [
      "lots",
      "snapshot",
      "lot-details",
      "lot-summary",
      `nav-stats-${entity.id}`,
    ],

    onSuccess: () => {
      const text = v({
        zero: t("Les lots ont bien été dupliqués !"),
        one: t("Le lot a bien été dupliqué !"),
        many: t("Les lots sélectionnés ont bien été dupliqués !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: () => {
      const text = v({
        zero: t("Les lots n'ont pas pu être dupliqués !"),
        one: t("Le lot n'a pas pu être dupliqué !"),
        many: t("Les lots sélectionnés n'ont pas pu être dupliqués !"),
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
            zero: t("Dupliquer tous les lots"),
            one: t("Dupliquer ce lot"),
            many: t("Dupliquer les lots sélectionnés"),
          })}
        </h1>
      </header>
      <main>
        <section>
          {v({
            zero: t("Voulez-vous dupliquer ces lots ?"),
            one: t("Voulez-vous dupliquer ce lot ?"),
            many: t("Voulez-vous dupliquer les lots sélectionnés ?"),
          })}
        </section>
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          autoFocus
          loading={duplicateLots.loading}
          variant="primary"
          icon={Copy}
          label={t("Dupliquer")}
          action={() => {
            matomo.push([
              "trackEvent",
              "lots",
              "duplicate-lot",
              selection.length,
            ])
            duplicateLots.execute(query.entity_id, selection[0] as number)
          }}
        />
        <Button
          disabled={duplicateLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
      </footer>
    </Dialog>
  )
}
