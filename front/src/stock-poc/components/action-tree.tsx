import { Text } from "common/components/text"
import { Fragment } from "react"
import { useTranslation } from "react-i18next"
import { ActionNode } from "../utils"
import css from "./action-tree.module.css"
import { Collapse } from "common/components/collapse2"

const INDENT_REM = 1.5

const ActionTreeNodeLabel = ({
  node,
  path,
  depth,
}: {
  node: ActionNode
  path: string
  depth: number
}) => {
  return (
    <div
      className={css.line}
      style={{ paddingLeft: `${depth * INDENT_REM}rem` }}
    >
      <Text className={css.label}>{`action ${path}`}</Text>
      <Text>{node.type}</Text>
      <Text>{node.quantity}</Text>
      <Text className={css.muted}>({node.available} dispo)</Text>
      <Text>{node.status ?? "—"}</Text>
      <Text className={css.muted}>{node.owner_name}</Text>
    </div>
  )
}
const ActionTreeNode = ({
  node,
  path,
  depth,
}: {
  node: ActionNode
  path: string
  depth: number
}) => {
  return (
    <Collapse
      label={<ActionTreeNodeLabel node={node} path={path} depth={depth} />}
    >
      {node.children.map((child, index) => (
        <ActionTreeNode
          key={child.id}
          node={child}
          path={`${path}.${index + 1}`}
          depth={depth + 1}
        />
      ))}
    </Collapse>
  )
}

export const ActionTree = ({
  roots,
  loading,
}: {
  roots: ActionNode[]
  loading?: boolean
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
        <Collapse
          label={
            <ActionTreeNodeLabel
              node={root}
              path={String(index + 1)}
              depth={0}
            />
          }
          key={root.id}
        >
          {root.children.map((child, index) => (
            <ActionTreeNode
              key={child.id}
              node={child}
              path={`${String(index + 1)}.${index + 1}`}
              depth={1}
            />
          ))}
        </Collapse>
      ))}
    </div>
  )
}
