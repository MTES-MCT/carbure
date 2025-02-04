import { EntityType, Notification, NotificationType } from "carbure/types"
import { formatDate, formatPeriod } from "common/utils/formatters"
import { useTranslation } from "react-i18next"

const getNotificationLink = (notif: Notification) => {
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

export const useNotifications = () => {
  const { t } = useTranslation()

  const getNotificationText = (notif: Notification) => {
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

  return { getNotificationText, getNotificationLink }
}
