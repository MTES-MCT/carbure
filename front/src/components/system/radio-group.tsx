import React from "react"

import { Box } from "."
import styles from "./radio-group.module.css"

type RadioGroupProps = {
  value: string
  options: { value: string; label: string }[]
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
}

const RadioGroup = ({ value, options, onChange }: RadioGroupProps) => (
  <Box className={styles.radioGroup}>
    {options.map((option) => (
      <label key={option.value} className={styles.radioGroupLabel}>
        <input
          type="radio"
          checked={option.value === value}
          value={option.value}
          className={styles.radioGroupButton}
          onChange={onChange}
        />
        {option.label}
      </label>
    ))}
  </Box>
)

export default RadioGroup
