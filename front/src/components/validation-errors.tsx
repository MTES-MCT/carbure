import React from "react"

import { ValidationError } from "../services/types"

import styles from "./validation-errors.module.css"

import { Collapsible } from "./system/alert"
import { AlertTriangle, AlertOctagon } from "./system/icons"

type ValidationErrorsProps = {
  validationErrors: ValidationError[]
}

const ValidationErrors = ({ validationErrors }: ValidationErrorsProps) => {
  const errors = validationErrors.filter((e) => e.is_blocking)
  const warnings = validationErrors.filter((e) => e.is_warning && !e.is_blocking) // prettier-ignore

  return (
    <React.Fragment>
      {errors.length > 0 && (
        <Collapsible
          icon={AlertOctagon}
          level="error"
          title={`Erreurs bloquantes (${errors.length})`}
          className={styles.transactionError}
        >
          <ul className={styles.validationErrors}>
            {errors.map((err, i) => (
              <li key={i}>{err.error || "Erreur de validation"}</li>
            ))}
          </ul>
        </Collapsible>
      )}

      {warnings.length > 0 && (
        <Collapsible
          icon={AlertTriangle}
          level="warning"
          title={`Erreurs non-bloquantes (${warnings.length})`}
          className={styles.transactionError}
        >
          <ul className={styles.validationErrors}>
            {warnings.map((err, i) => (
              <li key={i}>{err.error || "Erreur de validation"}</li>
            ))}
          </ul>
        </Collapsible>
      )}
    </React.Fragment>
  )
}

export default ValidationErrors
