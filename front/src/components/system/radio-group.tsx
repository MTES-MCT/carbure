import React from "react"

import { Box } from "."
import styles from "./radio-group.module.css"

type RadioGroupProps = {
  value: string
  name?: string
  row?: boolean
  readOnly?: boolean
  options: { value: string; label: string }[]
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
}

const RadioGroup = ({
  row,
  value,
  name,
  options,
  readOnly,
  onChange,
}: RadioGroupProps) => (
  <Box row={row} className={styles.radioGroup}>
    {options.map((option) => (
      <Box row as="label" key={option.value} className={styles.radioGroupLabel}>
        <input
          type="radio"
          disabled={readOnly}
          checked={option.value === value}
          value={option.value}
          name={name}
          className={styles.radioGroupButton}
          onChange={onChange}
        />
        {option.label}
      </Box>
    ))}
  </Box>
)

export default RadioGroup
