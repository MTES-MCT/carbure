import React from "react"
import { Trans, useTranslation } from "react-i18next"

import { GenericError } from "common/types"

import { Collapsible } from "common/components/alert"
import { AlertTriangle, AlertOctagon } from "common/components/icons"

import styles from "./form-errors.module.css"

type ValidationErrorsProps = {
  errors: GenericError[]
}

const ValidationErrors = ({ errors }: ValidationErrorsProps) => {
  const { t } = useTranslation("translation")

  const blocking = errors.filter((e) => e.is_blocking)
  const warnings = errors.filter((e) => !e.is_blocking)

  return (
    <React.Fragment>
      {blocking.length > 0 && (
        <Collapsible
          icon={AlertOctagon}
          level="error"
          title={t("Erreurs ({{amount}})", { amount: blocking.length })}
          className={styles.transactionError}
        >
          <span className={styles.transactionErrorExplanation}>
            <Trans>
              Vous ne pouvez pas valider ce lot tant que les problèmes suivants
              n'ont pas été adressés :
            </Trans>
          </span>
          <ul className={styles.validationErrors}>
            {blocking.map((err, i) => (
              <li key={i}>
                {t(err.error, { ns: "errors" }) || t("Erreur de validation")}{" "}
                {err.extra &&
                  err.extra !== t(err.error, { ns: "errors" }) &&
                  ` - ${err.extra}`}
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
          <span className={styles.transactionErrorExplanation}>
            <Trans>
              Des incohérences potentielles ont été détectées, elles n'empêchent
              pas la validation du lot mais peuvent donner lieu à un contrôle :
            </Trans>
          </span>
          <ul className={styles.validationErrors}>
            {warnings.map((err, i) => (
              <li key={i}>
                {t(err.error, { ns: "errors" }) || t("Erreur de validation")}
                {err.extra &&
                  err.extra !== t(err.error, { ns: "errors" }) &&
                  ` - ${err.extra}`}
              </li>
            ))}
          </ul>
        </Collapsible>
      )}
    </React.Fragment>
  )
}

export default ValidationErrors
