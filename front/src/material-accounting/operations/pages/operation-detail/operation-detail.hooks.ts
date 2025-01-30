import { useMutation } from "common/hooks/async"
import * as api from "./api"
import { useNotify } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { apiTypes } from "common/services/api-fetch.types"

type UseDeleteOperationProps = {
  operation?: apiTypes["OperationOutput"]
  onDeleteOperation: () => void
}

export const useDeleteOperation = ({
  operation,
  onDeleteOperation,
}: UseDeleteOperationProps) => {
  const notify = useNotify()
  const { t } = useTranslation()

  return useMutation(api.deleteOperation, {
    invalidates: ["operations"],
    onSuccess: () => {
      notify(t(`L'opération n°${operation?.id} a été annulée.`), {
        variant: "success",
      })
      onDeleteOperation()
    },
    onError: () => {
      notify(t(`L'opération n°${operation?.id} n'a pas pu être annulée.`), {
        variant: "danger",
      })
    },
  })
}

type UseAcceptOperationProps = {
  operation?: apiTypes["OperationOutput"]
  onAcceptOperation: () => void
}
export const useAcceptOperation = ({
  operation,
  onAcceptOperation,
}: UseAcceptOperationProps) => {
  const notify = useNotify()
  const { t } = useTranslation()

  return useMutation(api.acceptOperation, {
    invalidates: ["operations"],
    onSuccess: () => {
      notify(t(`L'opération n°${operation?.id} a été acceptée.`), {
        variant: "success",
      })
      onAcceptOperation()
    },
    onError: () => {
      notify(t(`L'opération n°${operation?.id} n'a pas pu être acceptée.`), {
        variant: "danger",
      })
    },
  })
}

type UseRejectOperationProps = {
  operation?: apiTypes["OperationOutput"]
  onRejectOperation: () => void
}

export const useRejectOperation = ({
  operation,
  onRejectOperation,
}: UseRejectOperationProps) => {
  const notify = useNotify()
  const { t } = useTranslation()

  return useMutation(api.rejectOperation, {
    invalidates: ["operations"],
    onSuccess: () => {
      notify(t(`L'opération n°${operation?.id} a été rejetée.`), {
        variant: "success",
      })
      onRejectOperation()
    },
    onError: () => {
      notify(t(`L'opération n°${operation?.id} n'a pas pu être rejetée.`), {
        variant: "danger",
      })
    },
  })
}
