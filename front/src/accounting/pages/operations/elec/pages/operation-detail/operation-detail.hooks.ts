import { useMutation } from "common/hooks/async"
import * as api from "accounting/api/elec/operations"
import { useNotify } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { ElecOperation } from "accounting/types"

type UseDeleteOperationProps = {
  operation?: ElecOperation
  onDeleteOperation: () => void
}

export const useDeleteOperation = ({
  operation,
  onDeleteOperation,
}: UseDeleteOperationProps) => {
  const notify = useNotify()
  const { t } = useTranslation()

  return useMutation(api.deleteOperation, {
    invalidates: ["elec-operations"],
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
  operation?: ElecOperation
  onAcceptOperation: () => void
}
export const useAcceptOperation = ({
  operation,
  onAcceptOperation,
}: UseAcceptOperationProps) => {
  const notify = useNotify()
  const { t } = useTranslation()

  return useMutation(api.acceptOperation, {
    invalidates: ["elec-operations"],
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
  operation?: ElecOperation
  onRejectOperation: () => void
}

export const useRejectOperation = ({
  operation,
  onRejectOperation,
}: UseRejectOperationProps) => {
  const notify = useNotify()
  const { t } = useTranslation()

  return useMutation(api.rejectOperation, {
    invalidates: ["elec-operations"],
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
