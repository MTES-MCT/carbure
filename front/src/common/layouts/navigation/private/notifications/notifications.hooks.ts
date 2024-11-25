import { EntityType, Notification, NotificationType } from "carbure/types"
import { formatDate, formatPeriod } from "common/utils/formatters"
import { useTranslation } from "react-i18next"

const getNotificationLink = (notif: Notification) => {
  switch (notif.type) {
    case NotificationType.LotsReceived:
      return `/org/${notif.dest.id}/transactions/${notif.meta?.year}/in/pending?suppliers=${notif.meta?.supplier}`

    case NotificationType.LotsRejected:
      return `/org/${notif.dest.id}/transactions/${notif.meta?.year}/out/correction?clients=${notif.meta?.client}`

    case NotificationType.LotsRecalled:
      return `/org/${notif.dest.id}/transactions/${notif.meta?.year}/in/correction?suppliers=${notif.meta?.supplier}`

    case NotificationType.CorrectionRequest:
      return `/org/${notif.dest.id}/transactions/${notif.meta?.year}/out/correction?clients=${notif.meta?.client}`

    case NotificationType.CorrectionDone:
      return `/org/${notif.dest.id}/transactions/${notif.meta?.year}/in/correction?suppliers=${notif.meta?.supplier}`

    case NotificationType.CertificateExpired:
      return `/org/${notif.dest.id}/settings#certificates`

    case NotificationType.CertificateRejected:
      return `/org/${notif.dest.id}/settings#certificates`

    case NotificationType.DeclarationValidated:
      return `#declaration/${notif.meta?.period}`

    case NotificationType.DeclarationCancelled:
      return `#declaration/${notif.meta?.period}`

    case NotificationType.MeterReadingsApplicationStarted:
      return `/org/${notif.dest.id}/settings#elec-meter-readings`
    case NotificationType.MeterReadingsApplicationEndingSoon:
      return `/org/${notif.dest.id}/settings#elec-meter-readings`
    case NotificationType.DeclarationReminder:
      return `#declaration/${notif.meta?.period}`

    case NotificationType.SafTicketReceived:
      if (notif.dest.entity_type === EntityType.Operator)
        return `/org/${notif.dest.id}/saf/${notif.meta?.year}/tickets-received/pending#ticket/${notif.meta?.ticket_id}`
      else
        return `/org/${notif.dest.id}/saf/${notif.meta?.year}/tickets/pending#ticket/${notif.meta?.ticket_id}`

    case NotificationType.SafTicketAccepted:
      if (notif.dest.entity_type === EntityType.Operator)
        return `/org/${notif.dest.id}/saf/${notif.meta?.year}/tickets-assigned/accepted#ticket/${notif.meta?.ticket_id}`
      else
        return `/org/${notif.dest.id}/saf/${notif.meta?.year}/tickets/accepted#ticket/${notif.meta?.ticket_id}`
    case NotificationType.SafTicketRejected:
      if (notif.dest.entity_type === EntityType.Operator)
        return `/org/${notif.dest.id}/saf/${notif.meta?.year}/tickets-assigned/rejected#ticket/${notif.meta?.ticket_id}`
      else
        return `/org/${notif.dest.id}/saf/${notif.meta?.year}/tickets/rejected#ticket/${notif.meta?.ticket_id}`

    default:
      return "#"
  }
}
export const useNotifications = () => {
  const { t } = useTranslation()

  const getNotificationText = (notif: Notification) => {
    switch (notif.type) {
      case NotificationType.LotsReceived:
        return t("Vous avez reçu {{count}} lots de {{supplier}}", {
          count: notif.meta?.count ?? 0,
          supplier: notif.meta?.supplier,
        })

      case NotificationType.LotsRejected:
        return t("Votre client {{client}} a refusé {{count}} lots", {
          count: notif.meta?.count ?? 0,
          client: notif.meta?.client,
        })

      case NotificationType.LotsRecalled:
        return t(
          "Votre fournisser {{supplier}} corrige des erreurs sur {{count}} lots",
          {
            count: notif.meta?.count ?? 0,
            supplier: notif.meta?.supplier,
          }
        )

      case NotificationType.CorrectionRequest:
        return t(
          "Vous avez reçu {{count}} demandes de correction de {{client}}",
          {
            count: notif.meta?.count,
            client: notif.meta?.client,
          }
        )

      case NotificationType.CorrectionDone:
        return t(
          "Votre fournisseur {{supplier}} a fini de corriger {{count}} lots",
          {
            count: notif.meta?.count ?? 0,
            supplier: notif.meta?.supplier,
          }
        )

      case NotificationType.CertificateExpired:
        return t("Votre certificat {{certificate}} est expiré", {
          certificate: notif.meta?.certificate,
        })

      case NotificationType.CertificateRejected:
        return t(
          "Votre certificat {{certificate}} a été refusé par l'administration",
          {
            certificate: notif.meta?.certificate,
          }
        )

      case NotificationType.DeclarationValidated:
        return t("Votre déclaration pour la période {{period}} a été validée", {
          period: formatPeriod(notif.meta?.period ?? 0),
        })

      case NotificationType.DeclarationCancelled:
        return t("Votre déclaration pour la période {{period}} a été annulée", {
          period: formatPeriod(notif.meta?.period ?? 0),
        })

      case NotificationType.DeclarationReminder:
        return t(
          "La période {{period}} arrive à sa fin, pensez à valider votre déclaration.",
          { period: formatPeriod(notif.meta?.period ?? 0) }
        )

      case NotificationType.MeterReadingsApplicationStarted:
        return t(
          "La période de declaration des relevés trimestriels T{{quarter}} {{year}} a débuté, vous avez jusqu'au {{deadline}} pour transmettre votre relevé dans votre espace.",
          {
            quarter: notif.meta.quarter,
            year: notif.meta.year,
            deadline: formatDate(notif.meta.deadline),
          }
        )
      case NotificationType.MeterReadingsApplicationEndingSoon:
        return t(
          "La période de declaration des relevés trimestriels T{{quarter}} {{year}} se termine bientôt, pensez à transmettre votre relevé rapidement.",
          { quarter: notif.meta.quarter, year: notif.meta.year }
        )

      case NotificationType.SafTicketReceived:
        return t("Vous avez reçu un ticket CAD de {{supplier}}.", {
          supplier: notif.meta.supplier,
        })
      case NotificationType.SafTicketAccepted:
        return t("Votre ticket a été accepté par {{client}}.", {
          client: notif.meta.client,
        })
      case NotificationType.SafTicketRejected:
        return t("Votre ticket a été refusé par {{client}}.", {
          client: notif.meta.client,
        })
      case NotificationType.LotsUpdatedByAdmin:
        return t(
          "{{count}} lots que vous avez déclarés ont été corrigés par l'administration avec le commentaire “{{comment}}”.",
          {
            count: notif.meta.updated,
            comment: notif.meta.comment,
          }
        )
      case NotificationType.LotsDeletedByAdmin:
        return t(
          "{{count}} lots que vous avez déclarés ont été supprimés par l'administration.",
          {
            count: notif.meta.deleted,
          }
        )

      default:
        return ""
    }
  }

  return { getNotificationText, getNotificationLink }
}
