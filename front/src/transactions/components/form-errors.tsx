import React from "react"

import { ValidationError } from "common/types"

import { Collapsible } from "common/components/alert"
import { AlertTriangle, AlertOctagon } from "common/components/icons"

import styles from "./form-errors.module.css"

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
          title={`Erreurs (${errors.length})`}
          className={styles.transactionError}
        >
          <i className={styles.transactionErrorExplanation}>
            Vous ne pouvez pas valider ce lot tant que les problèmes suivants
            n'ont pas été adressés :
          </i>
          <ul className={styles.validationErrors}>
            {errors.map((err, i) => (
              <li key={i}>{err.error || "Erreur de validation"} { err.details && ` - ${err.details}` }</li>
            ))}
          </ul>
        </Collapsible>
      )}

      {warnings.length > 0 && (
        <Collapsible
          icon={AlertTriangle}
          level="warning"
          title={`Remarques (${warnings.length})`}
          className={styles.transactionError}
        >
          <i className={styles.transactionErrorExplanation}>
            Des incohérences potentielles ont été détectées, elles n'empêchent
            pas la validation du lot mais peuvent donner lieu à un contrôle :
          </i>
          <ul className={styles.validationErrors}>
            {warnings.map((err, i) => (
              <li key={i}>{err.error || "Erreur de validation"} { err.details && ` - ${err.details}` }</li>
            ))}
          </ul>
        </Collapsible>
      )}
    </React.Fragment>
  )
}

export default ValidationErrors
