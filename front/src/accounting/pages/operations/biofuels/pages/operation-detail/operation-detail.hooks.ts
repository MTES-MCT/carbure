import { useMutation } from "common/hooks/async"
import * as api from "accounting/api/biofuels/operations"
import { useNotify } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { Operation, OperationType } from "accounting/types"
import { Depot } from "common/types"
import useEntity from "common/hooks/entity"

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
  onAcceptOperation?: () => void
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
      onAcceptOperation?.()
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

export const useValidateDraftTransfer = ({
  onSuccess,
}: {
  onSuccess?: () => void
}) => {
  const notify = useNotify()
  const { t } = useTranslation()

  const mutation = useMutation(api.patchOperation, {
    invalidates: ["operations"],
    onSuccess: () => {
      notify(
        t(
          "L'opération a bien été envoyée et est en attente de validation par l'administration."
        ),
        {
          variant: "success",
        }
      )
      onSuccess?.()
    },
    onError: () => {
      notify(t("Une erreur est survenue lors de l'opération."), {
        variant: "danger",
      })
    },
  })

  return mutation
}

/**
 * If the operation is an acquisition, the receiver can update the depot of delivery.
 * We need to patch the operation to update the depot of delivery and then accept the operation.
 * If the operation is not an acquisition, we just accept the operation.
 */
export const usePatchBeforeAcceptOperation = ({
  operation,
  onSuccess,
}: {
  operation?: Operation
  onSuccess: () => void
}) => {
  const notify = useNotify()
  const { t } = useTranslation()
  const entity = useEntity()
  const { execute: acceptOperation } = useAcceptOperation({
    operation,
    onAcceptOperation: onSuccess,
  })

  const { execute: patchOperation } = useMutation(api.patchOperation, {
    onError: () => {
      notify(
        t("Une erreur est survenue lors de la mise à jour de l'opération."),
        {
          variant: "danger",
        }
      )
    },
  })

  const onPatchBeforeAcceptOperation = (value: {
    to_depot?: Pick<Depot, "id" | "name">
  }) => {
    const patch = () => {
      if (
        operation &&
        operation.type === OperationType.ACQUISITION &&
        value.to_depot?.id !== operation?.to_depot?.id
      ) {
        return patchOperation(entity.id, operation?.id, {
          to_depot: value.to_depot?.id,
        })
      }
      return Promise.resolve()
    }

    if (!operation) {
      return Promise.reject(new Error("Operation not found"))
    }

    return patch().then(() => acceptOperation(entity.id, operation.id))
  }

  const mutation = useMutation(onPatchBeforeAcceptOperation, {
    onSuccess,
  })

  return mutation
}
