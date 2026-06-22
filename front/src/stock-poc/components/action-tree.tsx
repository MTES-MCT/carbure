import { Button } from "common/components/button2"
import { Collapse } from "common/components/collapse2"
import { Row } from "common/components/scaffold"
import { Text } from "common/components/text"
import { useTranslation } from "react-i18next"
import { Action } from "../types"
import { ActionNode } from "../utils"
import css from "./action-tree.module.css"

const INDENT_REM = 1.5

const ActionLine = ({
  node,
  path,
  depth = 0,
  onEdit,
  onDelete,
}: {
  node: ActionNode
  path: string
  depth?: number
  onEdit?: (action: Action) => void
  onDelete?: (action: Action) => void
}) => {
  const { t } = useTranslation()

  return (
    <div
      className={css.line}
      style={{ paddingLeft: `${depth * INDENT_REM}rem` }}
    >
      <Text>#{node.id}</Text>
      <Text className={css.label}>{`action ${path}`}</Text>
      <Text>{node.type}</Text>
      <Text>{node.quantity}</Text>
      <Text>{node.status ?? "—"}</Text>
      <Text className={css.muted}>{node.owner_name}</Text>
      {(onEdit || onDelete) && (
        <Row gap="sm" className={css.actions}>
          {onEdit && (
            <Button
              priority="tertiary no outline"
              iconId="ri-pencil-line"
              title={t("Modifier")}
              size="small"
              onClick={(e) => {
                e.stopPropagation()
                onEdit(node)
              }}
            />
          )}
          {onDelete && (
            <Button
              priority="tertiary no outline"
              iconId="ri-delete-bin-line"
              title={t("Supprimer")}
              size="small"
              onClick={(e) => {
                e.stopPropagation()
                onDelete(node)
              }}
            />
          )}
        </Row>
      )}
    </div>
  )
}

const ActionTreeBranch = ({
  node,
  path,
  depth,
  onEdit,
  onDelete,
}: {
  node: ActionNode
  path: string
  depth: number
  onEdit?: (action: Action) => void
  onDelete?: (action: Action) => void
}) => (
  <>
    <ActionLine
      node={node}
      path={path}
      depth={depth}
      onEdit={onEdit}
      onDelete={onDelete}
    />
    {node.children.map((child, index) => (
      <ActionTreeBranch
        key={child.id}
        node={child}
        path={`${path}.${index + 1}`}
        depth={depth + 1}
        onEdit={onEdit}
        onDelete={onDelete}
      />
    ))}
  </>
)

const ActionTreeRoot = ({
  node,
  path,
  onEdit,
  onDelete,
}: {
  node: ActionNode
  path: string
  onEdit?: (action: Action) => void
  onDelete?: (action: Action) => void
}) => (
  <Collapse
    className={css.rootCollapse}
    label={
      <ActionLine node={node} path={path} onEdit={onEdit} onDelete={onDelete} />
    }
  >
    {node.children.length > 0 && (
      <div className={css.subtree}>
        {node.children.map((child, index) => (
          <ActionTreeBranch
            key={child.id}
            node={child}
            path={`${path}.${index + 1}`}
            depth={1}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        ))}
      </div>
    )}
  </Collapse>
)

export const ActionTree = ({
  roots,
  loading,
  onEdit,
  onDelete,
}: {
  roots: ActionNode[]
  loading?: boolean
  onEdit?: (action: Action) => void
  onDelete?: (action: Action) => void
}) => {
  const { t } = useTranslation()

  if (loading) {
    return (
      <Text className={css.empty} size="sm">
        {t("Chargement…")}
      </Text>
    )
  }

  if (roots.length === 0) {
    return (
      <Text className={css.empty} size="sm">
        {t("Aucune action.")}
      </Text>
    )
  }

  return (
    <div className={css.tree}>
      {roots.map((root, index) => (
        <ActionTreeRoot
          key={root.id}
          node={root}
          path={String(index + 1)}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  )
}
