import React from "react"

import { GenericError } from "common/types"

import { Collapsible } from "common/components/alert"
import { AlertTriangle, AlertOctagon } from "common/components/icons"

import styles from "./form-errors.module.css"
import { useTranslation } from "react-i18next"

type ValidationErrorsProps = {
  errors: GenericError[]
}

const ValidationErrors = ({ errors }: ValidationErrorsProps) => {
  const { t } = useTranslation("errors")

  const blocking = errors.filter((e) => e.is_blocking)
  const warnings = errors.filter((e) => !e.is_blocking)

  return (
    <React.Fragment>
      {blocking.length > 0 && (
        <Collapsible
          icon={AlertOctagon}
          level="error"
          title={`Erreurs (${blocking.length})`}
          className={styles.transactionError}
        >
          <i className={styles.transactionErrorExplanation}>
            Vous ne pouvez pas valider ce lot tant que les problèmes suivants
            n'ont pas été adressés :
          </i>
          <ul className={styles.validationErrors}>
            {blocking.map((err, i) => (
              <li key={i}>
                {t(err.error) || "Erreur de validation"}{" "}
                {err.extra && err.extra !== t(err.error) && ` - ${err.extra}`}
              </li>
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
              <li key={i}>
                {t(err.error) || "Erreur de validation"}
                {err.extra && err.extra !== t(err.error) && ` - ${err.extra}`}
              </li>
            ))}
          </ul>
        </Collapsible>
      )}
    </React.Fragment>
  )
}

export default ValidationErrors
