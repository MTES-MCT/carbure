import React from "react"
import format from "date-fns/format"
import isBefore from "date-fns/isBefore"
import fr from "date-fns/locale/fr"

import { DBSCertificate, ISCCCertificate } from "../../services/types"

import styles from "./settings.module.css"
import { Box, BoxProps } from "../system"

export function formatDate(str: string) {
  try {
    const date = new Date(str)
    const formatted = format(date, "dd/MM/y", { locale: fr })
    return formatted
  } catch (e) {
    return "N/A"
  }
}

export function expiration(certificate: ISCCCertificate | DBSCertificate) {
  try {
    const now = new Date()
    const valid_until = new Date(certificate.valid_until)
    const formatted = formatDate(certificate.valid_until)

    return isBefore(valid_until, now)
      ? `Expiré depuis le ${formatted}`
      : formatted
  } catch (e) {
    return "N/A"
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

export const EMPTY_COLUMN = {
  className: styles.settingsTableEmptyColumn,
  render: () => null,
}
