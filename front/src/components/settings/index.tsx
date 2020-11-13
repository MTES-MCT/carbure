import React from "react"
import styles from "./settings.module.css"
import { Box, BoxProps } from "../system"

export const SettingsHeader = (props: BoxProps) => (
  <Box className={styles.settingsTop}>
    <Box {...props} className={styles.settingsHeader} />
  </Box>
)

export const SettingsBody = (props: BoxProps) => (
  <Box {...props} className={styles.settingsBody} />
)

export const EMPTY_COLUMN = {
  className: styles.settingsTableEmptyColumn,
  render: () => null,
}
