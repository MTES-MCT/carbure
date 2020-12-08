import React from "react"
import cl from "clsx"

import styles from "./section.module.css"

import { BoxProps, Box } from "."

export const Section = ({ className, ...props }: BoxProps) => (
  <Box {...props} as="section" className={cl(styles.section, className)} />
)

export const SectionHeader = (props: BoxProps) => (
  <Box {...props} row className={styles.sectionHeader} />
)

export const SectionBody = (props: BoxProps) => (
  <Box {...props} className={styles.sectionBody} />
)

export const SectionForm = (props: BoxProps) => (
  <Box {...props} as="form" className={styles.sectionForm} />
)
