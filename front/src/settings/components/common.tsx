import format from "date-fns/intlFormat"
import isBefore from "date-fns/isBefore"
import i18n from "i18n"

import styles from "./settings.module.css"
import { Box, BoxProps } from "common/components"

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
