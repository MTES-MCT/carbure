import * as api from "./api"
import { useMutation, useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useMatomo } from "matomo"
import { useNotifications } from "./notifications.hooks"
import { List } from "common/components/list2"
import { Normalizer } from "common/utils/normalize"
import { Notification } from "./types"
import { NavLink, useNavigate } from "react-router-dom"
import { formatDateTime, formatElapsedTime } from "common/utils/formatters"
import { Row } from "common/components/scaffold"
import cl from "clsx"
import { Text } from "common/components/text"
import { CircleFill } from "common/components/icon"
import { Button } from "common/components/button2"
import { Dropdown } from "common/components/dropdown2"
import { useRef } from "react"

import css from "./notifications.module.css"

export const Notifications = () => {
  const entity = useEntity()
  const matomo = useMatomo()
  const navigate = useNavigate()
  const ref = useRef<HTMLButtonElement>(null)

  const { getNotificationText, getNotificationLink } = useNotifications()

  const notifications = useQuery(api.getNotifications, {
    key: "notifications",
    params: [entity.id],
  })

  const ackNotifications = useMutation(api.ackNotifications)

  if (entity.id === -1) return null

  const items = notifications.result?.data ?? []

  const pending = items.filter((n) => !n.acked).map((n) => n.id)

  const handleOpenMenu = () => {
    matomo.push(["trackEvent", "notifications", "open"])
    if (pending.length > 0) {
      ackNotifications.execute(entity.id, pending)
    }
  }

  const handleCloseMenu = () => {
    // refetch notifications only when dropdown is closed
    notifications.execute(entity.id)
  }

  return (
    <>
      <Button
        priority="tertiary"
        iconId="ri-notification-3-line"
        size="small"
        title="Notifications"
        ref={ref}
      />
      <Dropdown
        triggerRef={ref}
        anchor="bottom end"
        onOpen={handleOpenMenu}
        onClose={handleCloseMenu}
        className={css["notifications-dropdown"]}
      >
        {({ close }) => (
          <List
            items={items}
            normalize={normalizeNotification}
            onSelectValue={(item) => {
              if (!item) return
              navigate(getNotificationLink(item))
              close()
            }}
            border={false}
          >
            {({ value: notif }) => (
              <NavLink
                className={css["notification-item-link"]}
                to={getNotificationLink(notif)}
                title={formatDateTime(notif.datetime)}
              >
                <Row
                  className={cl(
                    css["notification-item"],
                    !notif.acked && css["notification-item--pending"]
                  )}
                >
                  <div className={css["notification-item__content"]}>
                    <Text className={css["notification-item__elapsed-time"]}>
                      {formatElapsedTime(notif.datetime)}
                    </Text>
                    <Text is={Row} className={css["notification-item__text"]}>
                      {getNotificationText(notif)}
                    </Text>
                  </div>

                  {!notif.acked && (
                    <CircleFill
                      size="sm"
                      className={css["notification-item__icon"]}
                    />
                  )}
                </Row>
              </NavLink>
            )}
          </List>
        )}
      </Dropdown>
    </>
  )
}

const normalizeNotification: Normalizer<Notification> = (notif) => ({
  label: `${notif.id}`,
  value: notif,
})
