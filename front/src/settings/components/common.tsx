import React from "react"
import cl from "clsx"
import format from "date-fns/intlFormat"
import isBefore from "date-fns/isBefore"
import { Trans } from "react-i18next"
import i18n from "i18n"

import styles from "./settings.module.css"
import { Box, BoxProps } from "common/components"
import { Button } from "common/components/button"
import { Refresh } from "common/components/icons"

type FormatOptions = Parameters<typeof format>[1]

export const YEAR_ONLY = { month: undefined, day: undefined }

export function formatDate(str: string | null, options: FormatOptions = {}) {
  if (str === null) {
    return "N/A"
  }

  try {
    const formatted = format(
      new Date(str),
      {
        year: "numeric",
        month: "numeric",
        day: "numeric",
        ...options,
      },
      { locale: i18n.language === "en" ? "en-GB" : "fr" }
    )

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
          <Trans>Expiré ({{ formatted }})</Trans>
          {onUpdate && (
            <Button icon={Refresh} onClick={onClick}>
              <Trans>Mise à jour</Trans>
            </Button>
          )}
        </React.Fragment>
      )}

      {expired && updated && <Trans>Mis à jour ({{ formatted }})</Trans>}

      {!expired && formatted}
    </span>
  )
}
