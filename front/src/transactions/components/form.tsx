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
  errors?: { [k: string]: string }
  onChange: FormChangeHandler<TransactionFormState>
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void
}

const TransactionForm = ({
  id,
  entity,
  readOnly = false,
  transaction,
  error,
  errors = {},
  onChange,
  onSubmit,
}: TransactionFormProps) => {
  const isStock = Boolean(transaction.parent_lot)

  const isOwner =
    !transaction.data_origin_entity ||
    (Boolean(entity) && entity?.id === transaction.data_origin_entity?.id)

  return (
    <Form id={id} className={styles.transactionForm} onSubmit={onSubmit}>
      <Box row>
        <LotFields
          editable={isOwner && !isStock}
          readOnly={readOnly}
          data={transaction}
          errors={errors}
          onChange={onChange}
        />

        <OriginFields
          editable={isOwner && !isStock}
          readOnly={readOnly}
          entity={entity}
          data={transaction}
          errors={errors}
          onChange={onChange}
        />

        <ProductionFields
          readOnly={!isOwner || isStock || readOnly}
          entity={entity}
          data={transaction}
          errors={errors}
          onChange={onChange}
        />

        <DeliveryFields
          readOnly={readOnly}
          entity={entity}
          data={transaction}
          errors={errors}
          onChange={onChange}
        />

        <GESFields
          readOnly={!isOwner || isStock || readOnly}
          data={transaction}
          errors={errors}
          onChange={onChange}
        />
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
