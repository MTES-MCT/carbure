import React from "react"

import { TransactionOutSummaryFormState } from "../hooks/use-transaction-out-summary"

import styles from "./transaction-out-summary-form.module.css"

import { Box, LabelCheckbox, LabelInput, LabelTextArea } from "./system"
import { FormFields } from "../hooks/helpers/use-form"

type TransactionOutSummaryFormProps = {
  readOnly?: boolean
  data: TransactionOutSummaryFormState
  onChange: <T extends FormFields>(e: React.ChangeEvent<T>) => void
}

const TransactionOutSummaryForm = ({
  readOnly = false,
  onChange,
}: TransactionOutSummaryFormProps) => {
  return (
      <Box row>
        <Box>
        </Box>
      </Box>
  )
}

export default TransactionOutSummaryForm
