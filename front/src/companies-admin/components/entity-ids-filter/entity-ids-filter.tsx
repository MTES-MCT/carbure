import Tag from "@codegouvfr/react-dsfr/Tag"
import { Button } from "common/components/button2"
import { Dropdown } from "common/components/dropdown2"
import { TextArea } from "common/components/inputs2"
import { useEffect, useRef, useState } from "react"
import { useTranslation } from "react-i18next"
import styles from "./entity-ids-filter.module.css"

export function countEntityIds(raw: string) {
  const seen = new Set<string>()
  for (const token of raw.split(/[\s,;]+/)) {
    if (/^\d+$/.test(token)) seen.add(token)
  }
  return seen.size
}

type EntityIdsFilterProps = {
  value: string
  onChange: (value: string) => void
}

export const EntityIdsFilter = ({ value, onChange }: EntityIdsFilterProps) => {
  const { t } = useTranslation()
  const triggerRef = useRef<HTMLButtonElement>(null)
  const [open, setOpen] = useState(false)
  const [draft, setDraft] = useState(value)
  const appliedCount = countEntityIds(value)
  const draftCount = countEntityIds(draft)

  useEffect(() => {
    setDraft(value)
  }, [value])

  return (
    <>
      <Button
        ref={triggerRef}
        priority="tertiary"
        iconId="fr-icon-arrow-down-s-line"
        iconPosition="right"
      >
        {appliedCount > 0 && (
          <Tag
            dismissible
            small
            nativeButtonProps={{
              // The filter button listens to the native click. React's onClick
              // runs too late to stop that, so the dismiss control is marked captive.
              "data-captive": true,
              onClick: (event) => {
                event.stopPropagation()
                event.preventDefault()
                onChange("")
              },
            }}
            className={styles.tag}
          >
            {appliedCount}
          </Tag>
        )}
        {t("Identifiants")}
      </Button>
      <Dropdown
        open={open}
        triggerRef={triggerRef}
        onToggle={setOpen}
        onClose={() => setDraft(value)}
        style={{ maxHeight: "none" }}
      >
        <div className={styles.panel}>
          <TextArea
            label={t("Coller une colonne d'identifiants")}
            value={draft}
            onChange={(next) => setDraft(next ?? "")}
            rows={8}
            placeholder={"1842\n1903\n2044"}
            hintText={t("{{count}} identifiants reconnus", {
              count: draftCount,
            })}
          />
          <div className={styles.actions}>
            <Button
              size="small"
              onClick={() => {
                onChange(draft)
                setOpen(false)
              }}
            >
              {t("Appliquer")}
            </Button>
          </div>
        </div>
      </Dropdown>
    </>
  )
}
