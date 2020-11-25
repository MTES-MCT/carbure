import React from "react"
import format from "date-fns/format"
import isBefore from "date-fns/isBefore"
import fr from "date-fns/locale/fr"
import cl from "clsx"

import styles from "./settings.module.css"
import { Box, BoxProps, Button } from "../system"
import { Refresh } from "../system/icons"

export function formatDate(str: string) {
  try {
    const date = new Date(str)
    const formatted = format(date, "dd/MM/y", { locale: fr })
    return formatted
  } catch (e) {
    return "N/A"
  }
}

export function isExpired(date: string) {
  try {
    const now = new Date()
    const valid_until = new Date(date)
    return isBefore(valid_until, now)
  } catch (e) {
    return false
  }
}

export const SettingsHeader = (props: BoxProps) => (
  <Box className={styles.settingsTop}>
    <Box {...props} className={styles.settingsHeader} />
  </Box>
)

export const SettingsBody = (props: BoxProps) => (
  <Box {...props} className={styles.settingsBody} />
)

export const SettingsForm = (props: BoxProps) => (
  <Box {...props} as="form" className={styles.settingsForm} />
)

export const ExpirationDate = ({ date }: { date: string }) => {
  const expired = isExpired(date)
  const formatted = formatDate(date)

  return (
    <span className={cl(styles.expirationDate, expired && styles.expired)}>
      {expired && (
        <React.Fragment>
          Expiré depuis le {formatted}
          <Button icon={Refresh}>Mise à jour</Button>
        </React.Fragment>
      )}

      {!expired && formatted}
    </span>
  )
}

export const EMPTY_COLUMN = {
  className: styles.settingsTableEmptyColumn,
  render: () => null,
}
