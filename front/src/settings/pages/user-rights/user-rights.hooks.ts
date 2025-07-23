import useEntity from "common/hooks/entity"
import { useMutation, useQuery } from "common/hooks/async"
import * as api from "../../api/user-rights"
import { useTranslation } from "react-i18next"
import { useNotify } from "common/components/notifications"

export const useGetEntityRights = () => {
  const entity = useEntity()

  const response = useQuery(api.getEntityRights, {
    key: "entity-rights",
    params: [entity.id],
  })

  return {
    rights: response.result?.data?.requests ?? [],
    response,
  }
}

export const useChangeUserRole = () => {
  const { t } = useTranslation()
  const notify = useNotify()

  return useMutation(api.changeUserRole, {
    invalidates: ["entity-rights"],

    onSuccess: () => {
      notify(t("Le rôle de l'utilisateur a été modifié !"), {
        variant: "success",
      })
    },
    onError: () => {
      notify(t("Le rôle de l'utilisateur n'a pas pu être modifié !"), {
        variant: "danger",
      })
    },
  })
}

export const useRevokeUserRights = () =>
  useMutation(api.revokeUserRights, {
    invalidates: ["entity-rights"],
  })

export const useAcceptUserRights = () =>
  useMutation(api.acceptUserRightsRequest, {
    invalidates: ["entity-rights"],
  })

export const useInviteUser = () => {
  return useMutation(api.inviteUser, {
    invalidates: ["entity-rights"],
  })
}
