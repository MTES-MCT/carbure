import React from "react"

import { FormChangeHandler } from "common/hooks/use-form"
import { EntitySelection } from "carbure/hooks/use-entity"
import { TransactionFormState } from "../hooks/use-transaction-form"

import styles from "./form.module.css"

import { Box } from "common/components"
import { Alert } from "common/components/alert"
import { AlertTriangle } from "common/components/icons"

import { Form } from "common/components/form"
import LotFields from "./form/lot-fields"
import GESFields from "./form/ges-fields"
import ProductionFields from "./form/production-fields"
import DeliveryFields from "./form/delivery-fields"
import OriginFields from "./form/origin-fields"

type TransactionFormProps = {
  id?: string
  entity: EntitySelection
  readOnly?: boolean
  transaction: TransactionFormState
  error: string | null
  fieldErrors?: { [k: string]: string }
  onChange: FormChangeHandler<TransactionFormState>
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void
}

const TransactionForm = ({
  id,
  entity,
  readOnly = false,
  transaction,
  error,
  fieldErrors = {},
  onChange,
  onSubmit,
}: TransactionFormProps) => {
  return (
    <Form id={id} className={styles.transactionForm} onSubmit={onSubmit}>
      <Box row>
        <Box>
          <Box row>
            <LotFields
              readOnly={readOnly}
              data={transaction}
              errors={fieldErrors}
              onChange={onChange}
            />

            <OriginFields
              readOnly={readOnly}
              entity={entity}
              data={transaction}
              errors={fieldErrors}
              onChange={onChange}
            />

            <ProductionFields
              readOnly={readOnly}
              entity={entity}
              data={transaction}
              errors={fieldErrors}
              onChange={onChange}
            />

            <DeliveryFields
              readOnly={readOnly}
              entity={entity}
              data={transaction}
              errors={fieldErrors}
              onChange={onChange}
            />
          </Box>

          <span className={styles.transactionRequiredInfo}>
            * Les champs marqués d'une étoile sont obligatoires
          </span>
        </Box>

        <GESFields readOnly={readOnly} data={transaction} onChange={onChange} />
      </Box>

      {error && (
        <Alert
          level="error"
          icon={AlertTriangle}
          className={styles.transactionError}
        >
          {error}
        </Alert>
      )}
    </Form>
  )
}

export default TransactionForm
