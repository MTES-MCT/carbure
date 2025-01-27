import cl from "clsx"
import { Link } from "react-router-dom"
import { useNavigate } from "react-router-dom"
import { useMatomo } from "matomo"
import useEntity from "carbure/hooks/entity"
import Dropdown from "common/components/dropdown"
import { Bell, Check, Loader } from "common/components/icons"
import css from "./notifications.module.css"
import Button from "common/components/button"
import { useRef } from "react"
import List from "common/components/list"
import { EntityType, Notification, NotificationType } from "carbure/types"
import { Normalizer } from "common/utils/normalize"
import { t } from "i18next"
import Radio from "common/components/radio"
import { Col, Row } from "common/components/scaffold"
import {
  formatDate,
  formatDateTime,
  formatElapsedTime,
  formatPeriod,
} from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { useMutation, useQuery } from "common/hooks/async"
import * as api from "../api"

const Notifications = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const matomo = useMatomo()
  const triggerRef = useRef<HTMLButtonElement>(null)

  const entity = useEntity()

  const notifications = useQuery(api.getNotifications, {
    key: "notifications",
    params: [entity.id],
  })

  const ackNotifications = useMutation(api.ackNotifications, {
    invalidates: ["notifications"],
  })

  if (entity.id === -1) return null

  const items = notifications.result?.data ?? []
  const pending = items.filter((n) => !n.acked).map((n) => n.id)

  return (
    <>
      <Button
        domRef={triggerRef}
        variant="icon"
        className={css.notifications}
        title={t("Notifications")}
        icon={
          <NotificationIcon
            loading={notifications.loading}
            pending={pending.length}
          />
        }
      />

      <Dropdown
        className={css.notificationMenu}
        triggerRef={triggerRef}
        anchor="bottom end"
        onOpen={() => matomo.push(["trackEvent", "notifications", "open"])}
      >
        {({ close }) => (
          <>
            {pending.length > 0 && (
              <Button
                variant="link"
                className={css.markAllAsRead}
                action={() => ackNotifications.execute(entity.id, pending)}
              >
                <p>{t("Marquer tout comme lu")}</p>
                <Check />
              </Button>
            )}
            <List
              controlRef={triggerRef}
              className={css.items}
              items={items}
              normalize={normalizeNotification}
              onSelectValue={(item) => {
                if (!item) return
                if (!item.acked) ackNotifications.execute(entity.id, [item.id])
                navigate(getNotificationLink(item))
                close()
              }}
            >
              {({ value: notif }) => (
                <Link
                  style={{ flex: 1 }}
                  to={getNotificationLink(notif)}
                  title={formatDateTime(notif.datetime)}
                >
                  <Col>
                    <p className={css.notificationTime}>
                      {formatElapsedTime(notif.datetime)}
                    </p>
                    <Row
                      className={cl(
                        css.notificationText,
                        !notif.acked && css.pending
                      )}
                    >
                      {getNotificationText(notif)}
                      <Radio readOnly checked={!notif.acked} />
                    </Row>
                  </Col>
                </Link>
              )}
            </List>
          </>
        )}
      </Dropdown>
    </>
  )
}

interface NotificationIconProps {
  loading: boolean
  pending: number
}

const NotificationIcon = ({ loading, pending }: NotificationIconProps) => {
  if (loading) return <Loader />

  return (
    <div className={cl(css.notificationIcon, pending > 0 && css.pending)}>
      <Bell />
    </div>
  )
}

const normalizeNotification: Normalizer<Notification> = (notif) => ({
  label: `${notif.id}`,
  value: notif,
})

function getNotificationText(notif: Notification) {
  const meta = notif.meta as any

  switch (notif.type) {
    case NotificationType.LOTS_RECEIVED:
      return t("Vous avez reçu {{count}} lots de {{supplier}}", {
        count: meta?.count ?? 0,
        supplier: meta?.supplier,
      })

    case NotificationType.LOTS_REJECTED:
      return t("Votre client {{client}} a refusé {{count}} lots", {
        count: meta?.count ?? 0,
        client: meta?.client,
      })

    case NotificationType.LOTS_RECALLED:
      return t(
        "Votre fournisser {{supplier}} corrige des erreurs sur {{count}} lots",
        {
          count: meta?.count ?? 0,
          supplier: meta?.supplier,
        }
      )

    case NotificationType.CORRECTION_REQUEST:
      return t(
        "Vous avez reçu {{count}} demandes de correction de {{client}}",
        {
          count: meta?.count,
          client: meta?.client,
        }
      )

    case NotificationType.CORRECTION_DONE:
      return t(
        "Votre fournisseur {{supplier}} a fini de corriger {{count}} lots",
        {
          count: meta?.count ?? 0,
          supplier: meta?.supplier,
        }
      )

    case NotificationType.CERTIFICATE_EXPIRED:
      return t("Votre certificat {{certificate}} est expiré", {
        certificate: meta?.certificate,
      })

    case NotificationType.CERTIFICATE_REJECTED:
      return t(
        "Votre certificat {{certificate}} a été refusé par l'administration",
        {
          certificate: meta?.certificate,
        }
      )

    case NotificationType.DECLARATION_VALIDATED:
      return t("Votre déclaration pour la période {{period}} a été validée", {
        period: formatPeriod(meta?.period ?? 0),
      })

    case NotificationType.DECLARATION_CANCELLED:
      return t("Votre déclaration pour la période {{period}} a été annulée", {
        period: formatPeriod(meta?.period ?? 0),
      })

    case NotificationType.DECLARATION_REMINDER:
      return t(
        "La période {{period}} arrive à sa fin, pensez à valider votre déclaration.",
        { period: formatPeriod(meta?.period ?? 0) }
      )

    case NotificationType.METER_READINGS_APP_STARTED:
      return t(
        "La période de declaration des relevés trimestriels T{{quarter}} {{year}} a débuté, vous avez jusqu'au {{deadline}} pour transmettre votre relevé dans votre espace.",
        {
          quarter: meta.quarter,
          year: meta.year,
          deadline: formatDate(meta.deadline),
        }
      )
    case NotificationType.METER_READINGS_APP_ENDING_SOON:
      return t(
        "La période de declaration des relevés trimestriels T{{quarter}} {{year}} se termine bientôt, pensez à transmettre votre relevé rapidement.",
        { quarter: meta.quarter, year: meta.year }
      )

    case NotificationType.SAF_TICKET_RECEIVED:
      return t("Vous avez reçu un ticket CAD de {{supplier}}.", {
        supplier: meta.supplier,
      })
    case NotificationType.SAF_TICKET_ACCEPTED:
      return t("Votre ticket a été accepté par {{client}}.", {
        client: meta.client,
      })
    case NotificationType.SAF_TICKET_REJECTED:
      return t("Votre ticket a été refusé par {{client}}.", {
        client: meta.client,
      })
    case NotificationType.LOTS_UPDATED_BY_ADMIN:
      return t(
        "{{count}} lots que vous avez déclarés ont été corrigés par l'administration avec le commentaire “{{comment}}”.",
        {
          count: meta.updated,
          comment: meta.comment,
        }
      )
    case NotificationType.LOTS_DELETED_BY_ADMIN:
      return t(
        "{{count}} lots que vous avez déclarés ont été supprimés par l'administration.",
        {
          count: meta.deleted,
        }
      )

    default:
      return ""
  }
}

function getNotificationLink(notif: Notification) {
  const meta = notif.meta as any

  switch (notif.type) {
    case NotificationType.LOTS_RECEIVED:
      return `/org/${notif.dest.id}/transactions/${meta?.year}/in/pending?suppliers=${meta?.supplier}`

    case NotificationType.LOTS_REJECTED:
      return `/org/${notif.dest.id}/transactions/${meta?.year}/out/correction?clients=${meta?.client}`

    case NotificationType.LOTS_RECALLED:
      return `/org/${notif.dest.id}/transactions/${meta?.year}/in/correction?suppliers=${meta?.supplier}`

    case NotificationType.CORRECTION_REQUEST:
      return `/org/${notif.dest.id}/transactions/${meta?.year}/out/correction?clients=${meta?.client}`

    case NotificationType.CORRECTION_DONE:
      return `/org/${notif.dest.id}/transactions/${meta?.year}/in/correction?suppliers=${meta?.supplier}`

    case NotificationType.CERTIFICATE_EXPIRED:
      return `/org/${notif.dest.id}/settings#certificates`

    case NotificationType.CERTIFICATE_REJECTED:
      return `/org/${notif.dest.id}/settings#certificates`

    case NotificationType.DECLARATION_VALIDATED:
      return `#declaration/${meta?.period}`

    case NotificationType.DECLARATION_CANCELLED:
      return `#declaration/${meta?.period}`

    case NotificationType.METER_READINGS_APP_STARTED ||
      NotificationType.METER_READINGS_APP_ENDING_SOON:
      return `/org/${notif.dest.id}/settings#elec-meter-readings`

    case NotificationType.DECLARATION_REMINDER:
      return `#declaration/${meta?.period}`

    case NotificationType.SAF_TICKET_RECEIVED:
      if (notif.dest.entity_type === EntityType.Operator)
        return `/org/${notif.dest.id}/saf/${meta?.year}/tickets-received/pending#ticket/${meta?.ticket_id}`
      else
        return `/org/${notif.dest.id}/saf/${meta?.year}/tickets/pending#ticket/${meta?.ticket_id}`

    case NotificationType.SAF_TICKET_ACCEPTED:
      if (notif.dest.entity_type === EntityType.Operator)
        return `/org/${notif.dest.id}/saf/${meta?.year}/tickets-assigned/accepted#ticket/${meta?.ticket_id}`
      else
        return `/org/${notif.dest.id}/saf/${meta?.year}/tickets/accepted#ticket/${meta?.ticket_id}`
    case NotificationType.SAF_TICKET_REJECTED:
      if (notif.dest.entity_type === EntityType.Operator)
        return `/org/${notif.dest.id}/saf/${meta?.year}/tickets-assigned/rejected#ticket/${meta?.ticket_id}`
      else
        return `/org/${notif.dest.id}/saf/${meta?.year}/tickets/rejected#ticket/${meta?.ticket_id}`

    default:
      return "#"
  }
}

export default Notifications
