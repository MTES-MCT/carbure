import { Button } from "common/components/button2"
import { Confirm } from "common/components/dialog2"
import { useNotify } from "common/components/notifications"
import { ActionBar, Box, Content, Main } from "common/components/scaffold"
import { Text } from "common/components/text"
import useEntity from "common/hooks/entity"
import { useMutation, useQuery } from "common/hooks/async"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { deleteAction, getActionTree, resetAllActions } from "./api"
import { ActionTree } from "./components/action-tree"
import {
  CreateActionDialog,
  INVALIDATES,
} from "./components/create-action-dialog"
import { EditActionDialog } from "./components/edit-action-dialog"

import { usePortal } from "common/components/portal"
import { Action } from "./types"
import { buildActionForest } from "./utils"

export const StockPoc = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()
  usePrivateNavigation(t("Stock POC (arborescence)"))

  const notify = useNotify()

  const tree = useQuery(getActionTree, {
    key: "stock-poc-tree",
    params: [entity.id],
  })

  const actionList = tree.result ?? []

  const treeRoots = useMemo(() => buildActionForest(actionList), [actionList])

  const resetMutation = useMutation(resetAllActions, {
    invalidates: INVALIDATES,
    onSuccess: () => {
      notify(t("Toutes les actions ont été supprimées."), {
        variant: "success",
      })
    },
    onError: () => {
      notify(t("La réinitialisation a échoué."), { variant: "danger" })
    },
  })

  const deleteMutation = useMutation(deleteAction, {
    invalidates: INVALIDATES,
    onSuccess: () => {
      notify(t("Action supprimée."), { variant: "success" })
    },
    onError: () => {
      notify(t("La suppression de l'action a échoué."), { variant: "danger" })
    },
  })

  const handleReset = () => {
    portal((close) => (
      <Confirm
        title={t("Réinitialiser toutes les actions")}
        description={t(
          "Toutes les actions du POC seront supprimées. Cette action est irréversible."
        )}
        confirm={t("Réinitialiser")}
        customVariant="danger"
        onClose={close}
        onConfirm={() => resetMutation.execute(entity.id).then(close)}
      />
    ))
  }

  const handleCreate = () => {
    portal((close) => (
      <CreateActionDialog
        entityId={entity.id}
        actions={actionList}
        onClose={close}
      />
    ))
  }

  const handleEdit = (action: Action) => {
    portal((close) => (
      <EditActionDialog
        entityId={entity.id}
        action={action}
        actions={actionList}
        onClose={close}
      />
    ))
  }

  const handleDelete = (action: Action) => {
    portal((close) => (
      <Confirm
        title={t("Supprimer l'action #{{id}}", { id: action.id })}
        description={t(
          "Cette action et toutes ses actions filles seront supprimées. Cette action est irréversible."
        )}
        confirm={t("Supprimer")}
        icon="ri-delete-bin-line"
        customVariant="danger"
        onClose={close}
        onConfirm={() =>
          deleteMutation.execute(entity.id, action.id).then(close)
        }
      />
    ))
  }

  return (
    <Main>
      <Content>
        <ActionBar>
          <ActionBar.Grow />
          <Button
            priority="secondary"
            iconId="ri-delete-bin-line"
            onClick={handleReset}
          >
            {t("Réinitialiser toutes les actions")}
          </Button>
          <Button iconId="ri-add-line" onClick={handleCreate}>
            {t("Créer une action")}
          </Button>
        </ActionBar>

        <Box>
          <Text is="h2" size="lg" fontWeight="bold">
            {t("Arborescence globale")}
          </Text>
          <ActionTree
            roots={treeRoots}
            loading={tree.loading}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </Box>
      </Content>
    </Main>
  )
}

export default StockPoc
