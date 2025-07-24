import useEntity from "common/hooks/entity"
import { useMutation, useQuery } from "common/hooks/async"
import * as api from "../../api/user-rights"
import { useTranslation } from "react-i18next"
import { useNotify } from "common/components/notifications"
import { EntityTypeEnum } from "api-schema"

export const useGetEntityRights = () => {
  const entity = useEntity()
  const { t } = useTranslation()
  const response = useQuery(api.getEntityRights, {
    key: "entity-rights",
    params: [entity.id],
  })

  const allRequests = response.result?.data?.requests ?? []

  // Split requests into auditors and others
  const auditors = allRequests.filter(
    (request) => request.entity.entity_type === EntityTypeEnum.Auditor
  )
  const users = allRequests.filter(
    (request) => request.entity.entity_type !== EntityTypeEnum.Auditor
  )

  return {
    rights: [
      {
        data: users,
      },
      {
        title: t("Auditeurs"),
        description: t(
          "Les auditeurs peuvent visualiser vos données pour mener leurs audits"
        ),
        data: auditors,
      },
    ].filter(({ data }) => data.length > 0),
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
