import cl from "clsx"
import { useNavigate } from "react-router-dom"
import useEntity from "carbure/hooks/entity"
import Dropdown, { Anchors } from "common-v2/components/dropdown"
import { Bell, Check, Loader } from "common-v2/components/icons"
import css from "./notifications.module.css"
import Button from "common-v2/components/button"
import { useRef } from "react"
import List from "common-v2/components/list"
import { EntityType, Notification, NotificationType } from "carbure/types"
import { Normalizer } from "common-v2/utils/normalize"
import { t } from "i18next"
import { Link } from "react-router-dom"
import Radio from "common-v2/components/radio"
import { Col, Row } from "common-v2/components/scaffold"
import { formatDateTime, formatElapsedTime } from "common-v2/utils/formatters"
import { useTranslation } from "react-i18next"
import { useMutation, useQuery } from "common-v2/hooks/async"
import * as api from "../api"

const FAKE_NOTIF: Notification = {
  id: 10,
  dest: {
    id: 10,
    name: "Producteur Test MTE",
    entity_type: EntityType.Producer,
    has_mac: false,
    has_stocks: false,
    has_trading: false,
    has_direct_deliveries: false,
  },
  datetime: "2022-03-14",
  type: NotificationType.LotsReceived,
  acked: false,
  send_by_email: false,
  email_sent: false,
  meta: {
    year: 2022,
    lots: 12,
    supplier: "Producteur Test MTE",
  },
}

const FAKE_NOTIFS = [
  FAKE_NOTIF,
  {
    ...FAKE_NOTIF,
    id: 20,
    date: "2022-03-13",
    meta: { ...FAKE_NOTIF.meta, lots: 245 },
  },
  {
    ...FAKE_NOTIF,
    id: 30,
    date: "2022-02-04",
    acked: true,
  },
  {
    ...FAKE_NOTIF,
    id: 40,
    date: "2020-01-01",
    acked: true,
  },
]

const Notifications = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
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

  const items = notifications.result?.data.data ?? []
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
        anchor={Anchors.bottomRight}
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
                !item.acked && ackNotifications.execute(entity.id, [item.id])
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
  switch (notif.type) {
    case NotificationType.LotsReceived:
      return t("Vous avez reçu {{count}} lots de {{supplier}}", {
        count: notif.meta?.count ?? 0,
        supplier: notif.meta?.supplier,
      })

    case NotificationType.LotsRejected:
      return t("Votre client {{client}} a rejeté {{count}} lots", {
        count: notif.meta?.count ?? 0,
        client: notif.meta?.client,
      })

    case NotificationType.LotsRecalled:
      return t("Votre fournisser {{supplier}} corrige des erreurs sur {{count}} lots", {
        count: notif.meta?.count ?? 0,
        supplier: notif.meta?.supplier,
      })

    case NotificationType.CorrectionRequest:
      return t("Vous avez reçu {{count}} demandes de correction de {{client}}", {
        count: notif.meta?.count,
        client: notif.meta?.client,
      })

    case NotificationType.CorrectionDone:
      return t("Votre fournisseur {{supplier}} a fini de corriger {{count}} lots", {
        count: notif.meta?.count ?? 0,
        supplier: notif.meta?.supplier,
      })

    case NotificationType.CertificateExpired:
      return t("Votre certificat {{certificate}} est expiré", {
        certificate: notif.meta?.certificate,
      })
  }
}

function getNotificationLink(notif: Notification) {
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
  }
}

export default Notifications
