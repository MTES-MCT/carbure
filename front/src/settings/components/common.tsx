import React from "react"
import format from "date-fns/format"
import isBefore from "date-fns/isBefore"
import fr from "date-fns/locale/fr"
import cl from "clsx"

import styles from "./settings.module.css"
import { Box, BoxProps } from "common/components"
import { Button } from "common/components/button"
import { Refresh } from "common/components/icons"

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

type ExpirationDateProps = {
  date: string
  updated: boolean
  onUpdate?: () => void
}

export const ExpirationDate = ({
  date,
  updated,
  onUpdate,
}: ExpirationDateProps) => {
  const expired = isExpired(date)
  const formatted = formatDate(date)

  function onClick(e: React.MouseEvent) {
    e.stopPropagation()
    onUpdate && onUpdate()
  }

  return (
    <span className={cl(styles.expirationDate, expired && styles.expired)}>
      {expired && !updated && (
        <React.Fragment>
          Expiré ({formatted})
          {onUpdate && (
            <Button icon={Refresh} onClick={onClick}>
              Mise à jour
            </Button>
          )}
        </React.Fragment>
      )}

      {expired && updated && `Mis à jour (${formatted})`}

      {!expired && formatted}
    </span>
  )
}
