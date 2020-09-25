import React from "react"

import styles from "./select.module.css"

import { SystemProps } from "../system"
import { Cross } from "../icons"
import { Dropdown, useDropdown } from "./dropdown"

export type Option = {
  key: string | number
  label: string
}

type SelectLabelProps = SystemProps & {
  value: Option | null
  placeholder?: string
  onChange: (value: Option | null) => void
}

type SelectProps = SelectLabelProps & {
  options: Option[]
}

export const Select = ({
  value,
  placeholder,
  options,
  onChange,
  children,
  ...props
}: SelectProps) => {
  const dd = useDropdown()

  function clear(e: React.MouseEvent) {
    e.stopPropagation()
    onChange(null)
  }

  return (
    <Dropdown {...props} onClick={dd.toggle}>
      <Dropdown.Label className={styles.selectLabel}>
        <span className={styles.selectValue}>
          {value?.label ?? placeholder}
        </span>

        {value && <Cross className={styles.selectCross} onClick={clear} />}
      </Dropdown.Label>

      <Dropdown.Items open={dd.isOpen}>
        {options.map((option) => (
          <li
            key={option.key}
            title={option.label}
            value={option.key}
            onClick={() => onChange(option)}
          >
            {option.label}
          </li>
        ))}
      </Dropdown.Items>
    </Dropdown>
  )
}

export default Select
