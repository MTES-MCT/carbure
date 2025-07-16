import {
  TagsGroup as TagsGroupDSFR,
  TagsGroupProps as TagsGroupPropsDSFR,
} from "@codegouvfr/react-dsfr/TagsGroup"
import { TagProps } from "@codegouvfr/react-dsfr/Tag"
import css from "./tags-group.module.css"
import cl from "clsx"
type TagsGroupProps = Omit<TagsGroupPropsDSFR, "tags"> & {
  tags: TagProps[]
}

// DSFR requires at least one tag, so to simplify the usage, we add a wrapper to handle empty array of tags
export const TagsGroup = ({ tags, ...props }: TagsGroupProps) => {
  if (tags.length === 0) return null

  const items = tags as [TagProps, ...TagProps[]]
  return (
    <TagsGroupDSFR
      tags={items}
      {...props}
      className={cl(props.className, css["tags-group"])}
    />
  )
}
