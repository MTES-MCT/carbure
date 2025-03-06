import { useMutation } from "common/hooks/async"
import * as api from "./api"
import { useNotify } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { Operation } from "accounting/operations/types"

type UseDeleteOperationProps = {
  operation?: Operation
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
      notify(t(`L'opération n°{{id}} a été annulée.`, { id: operation?.id }), {
        variant: "success",
      })
      onDeleteOperation()
    },
    onError: () => {
      notify(
        t(`L'opération n°{{id}} n'a pas pu être annulée.`, {
          id: operation?.id,
        }),
        {
          variant: "danger",
        }
      )
    },
  })
}

type UseAcceptOperationProps = {
  operation?: Operation
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
      notify(t(`L'opération n°{{id}} a été acceptée.`, { id: operation?.id }), {
        variant: "success",
      })
      onAcceptOperation()
    },
    onError: () => {
      notify(
        t(`L'opération n°{{id}} n'a pas pu être acceptée.`, {
          id: operation?.id,
        }),
        {
          variant: "danger",
        }
      )
    },
  })
}

type UseRejectOperationProps = {
  operation?: Operation
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
      notify(t(`L'opération n°{{id}} a été rejetée.`, { id: operation?.id }), {
        variant: "success",
      })
      onRejectOperation()
    },
    onError: () => {
      notify(
        t(`L'opération n°{{id}} n'a pas pu être rejetée.`, {
          id: operation?.id,
        }),
        {
          variant: "danger",
        }
      )
    },
  })
}
