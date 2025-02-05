import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Lot } from "../types"
import * as api from "../api"
import useEntity from "carbure/hooks/entity"
import { useMutation } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { variations } from "common/utils/formatters"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Cross, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LotSummary } from "../components/lots/lot-summary"
import { useStatus } from "transactions/components/status"
import { useMatomo } from "matomo"
import { AxiosError } from "axios"

export interface CancelAcceptManyButtonProps {
  disabled?: boolean
  selection: number[]
}

export const CancelAcceptManyButton = ({
  disabled,
  selection,
}: CancelAcceptManyButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      disabled={disabled || selection.length === 0}
      variant="danger"
      icon={Cross}
      label={t("Annuler l'acceptation")}
      action={() =>
        portal((close) => (
          <CancelAcceptDialog summary selection={selection} onClose={close} />
        ))
      }
    />
  )
}

export interface CancelAcceptOneButtonProps {
  icon?: boolean
  lot: Lot
}

export const CancelAcceptOneButton = ({
  icon,
  lot,
}: CancelAcceptOneButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <Button
      captive
      variant={icon ? "icon" : "danger"}
      icon={Cross}
      title={t("Annuler l'acceptation")}
      label={t("Annuler l'acceptation")}
      action={() =>
        portal((close) => (
          <CancelAcceptDialog selection={[lot.id]} onClose={close} />
        ))
      }
    />
  )
}

interface CancelAcceptDialogProps {
  summary?: boolean
  selection: number[]
  onClose: () => void
}

const CancelAcceptDialog = ({
  summary,
  selection,
  onClose,
}: CancelAcceptDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()
  const status = useStatus()
  const entity = useEntity()

  const v = variations(selection.length)

  const cancelAcceptLots = useMutation(api.cancelAcceptLots, {
    invalidates: [
      "lots",
      "snapshot",
      "lot-details",
      "lot-summary",
      `nav-stats-${entity.id}`,
    ],

    onSuccess: () => {
      const text = v({
        one: t("Le lot a bien été renvoyé dans la boîte de réception !"),
        many: t("Les lots ont bien été renvoyés dans la boîte de réception !"),
      })

      notify(text, { variant: "success" })
      onClose()
    },

    onError: (err) => {
      const error = (err as AxiosError<{ error: string }>).response?.data.error

      let text = v({
        one: t("Le lot n'a pas pu être renvoyé dans la boîte de réception !"),
        many: t("Les lots n'ont pas pu être renvoyés dans la boîte de réception !"), // prettier-ignore
      })

      text += " "

      if (error === "WRONG_STATUS") {
        text += v({
          one: t("Le lot n'a pas encore été accepté ou est déjà déclaré."), // prettier-ignore
          many: t("Certains lots n'ont pas encore été acceptés ou sont déjà déclarés."), // prettier-ignore
        })
      } else if (error === "CHILDREN_IN_USE") {
        text += v({
          one: t("Des lots ou stocks créés à partir de celui-ci ont déjà été utilisés."), // prettier-ignore
          many: t("Des lots ou stocks créés à partir de ceux-ci ont déjà été utilisés."), // prettier-ignore
        })
      }

      notify(text.trim(), { variant: "danger" })
      onClose()
    },
  })

  const query = useMemo(
    () => ({ status, entity_id: entity.id }),
    [status, entity.id]
  )

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>
          {v({
            one: t("Annuler l'acceptation du lot"),
            many: t("Annuler l'acceptation des lots"),
          })}
        </h1>
      </header>
      <main>
        <section>
          <p>
            {v({
              one: t(
                "Voulez-vous renvoyer le lot dans la boîte de réception ?"
              ),
              many: t(
                "Voulez-vous renvoyer les lots dans la boîte de réception ?"
              ),
            })}
          </p>
          <p>
            {t(
              "En confirmant cette opération, les lots sélectionnés retourneront dans l'état 'En attente' afin que vous puissiez à nouveau les accepter avec la bonne option."
            )}
          </p>
        </section>
        {summary && <LotSummary query={query} selection={selection} />}
      </main>
      <footer>
        <Button
          asideX
          autoFocus
          loading={cancelAcceptLots.loading}
          variant="danger"
          icon={Cross}
          label={t("Annuler l'acceptation")}
          action={() => {
            matomo.push([
              "trackEvent",
              "lots",
              "cancel-accept",
              selection.length,
            ])
            cancelAcceptLots.execute(entity.id, selection)
          }}
        />
        <Button
          disabled={cancelAcceptLots.loading}
          icon={Return}
          label={t("Annuler")}
          action={onClose}
        />
      </footer>
    </Dialog>
  )
}
