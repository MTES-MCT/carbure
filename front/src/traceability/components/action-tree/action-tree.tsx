import { useMemo } from "react"
import { useTranslation } from "react-i18next"

import { Dialog } from "common/components/dialog2"
import { Text } from "common/components/text"
import { ActionTreeNode } from "traceability/types"
import { getActionTypeLabel } from "traceability/utils/formatters"

import styles from "./action-tree.module.css"

type ActionTreeProps = {
  nodes: ActionTreeNode[]
  currentId: number
}

export const ActionTree = ({ nodes, currentId }: ActionTreeProps) => {
  const { t } = useTranslation()
  const childrenByParent = useMemo(() => {
    const grouped = new Map<number | null, ActionTreeNode[]>()
    for (const node of nodes) {
      const siblings = grouped.get(node.parent_id) ?? []
      siblings.push(node)
      grouped.set(node.parent_id, siblings)
    }
    return grouped
  }, [nodes])

  const renderNode = (node: ActionTreeNode) => {
    const children = childrenByParent.get(node.id) ?? []
    return (
      <li key={node.id}>
        <Text
          size="sm"
          fontWeight={node.id === currentId ? "bold" : "regular"}
          margin={false}
        >
          {node.id} · {getActionTypeLabel(node.type)} — {node.holder.name}
          {node.site ? ` — ${node.site.name}` : ""}
        </Text>
        {children.length > 0 && (
          <ul className={styles.branch}>{children.map(renderNode)}</ul>
        )}
      </li>
    )
  }

  const roots = childrenByParent.get(null) ?? []
  if (roots.length === 0) return null

  return (
    <Dialog.Section label={t("Arborescence")}>
      <ul className={styles.tree}>{roots.map(renderNode)}</ul>
    </Dialog.Section>
  )
}
