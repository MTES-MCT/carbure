import { TextInput } from "../inputs2"
import { useEffect, useMemo, useRef } from "react"
import css from "./tag-autocomplete.module.css"
import { Field } from "./field"
import { Dropdown, Trigger } from "../dropdown2"
import { InputProps } from "../inputs2/input"
import {
  defaultNormalizer,
  normalizeItems,
  Normalizer,
  Sorter,
} from "common/utils/normalize"
import { defaultRenderer, List, Renderer } from "../list2"
import { useTagAutocomplete } from "./tag-autocomplete.hooks"
import { Text } from "../text"
import { Trans } from "react-i18next"
import { LoaderLine } from "../icon"
import { multipleSelection } from "common/utils/selection"
import { TagsGroup } from "../tag2"

export type TagAutocompleteProps<T, V = T> = Trigger &
  InputProps & {
    value?: V[]
    options?: T[]
    defaultOptions?: T[]
    getOptions?: (query: string) => Promise<T[]>
    onChange: (value: V[] | undefined) => void
    onQuery?: (query: string) => Promise<T[] | void> | T[] | void
    normalize?: Normalizer<T, V>
    children?: Renderer<T, V>
    sort?: Sorter<T, V>
    debounce?: number
  }

export const TagAutocomplete = <T, V = T>({
  value = [],
  options,
  defaultOptions,
  getOptions,
  onChange,
  onQuery,
  normalize = defaultNormalizer,
  children = defaultRenderer,
  anchor,
  loading,
  placeholder,
  ...props
}: TagAutocompleteProps<T, V>) => {
  const ref = useRef<HTMLInputElement>(null)
  const tagsRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLInputElement>(null)

  const autocomplete = useTagAutocomplete({
    value,
    options,
    defaultOptions,
    getOptions,
    onChange,
    onQuery,
    normalize,
  })
  useEffect(() => {
    if (ref.current) {
      ref.current.style.paddingLeft = `calc(var(--spacing-2w) + ${tagsRef.current?.offsetWidth ?? 0}px)`
    }
  }, [autocomplete.tags])

  const tags = useMemo(() => {
    const normItems = normalizeItems(autocomplete.tags, normalize)
    const values = normItems.map((item) => item.value)
    const { onSelect } = multipleSelection(values, onChange)

    return normItems.map((item) => ({
      dismissible: true,
      children: item.label,
      nativeButtonProps: {
        onClick: () => onSelect(item.value),
        disabled: props.readOnly,
      },
    }))
  }, [autocomplete.tags, normalize, onChange, props.readOnly])

  return (
    <>
      <Field {...props}>
        <div className={css.container}>
          {tags.length > 0 ? (
            <div ref={tagsRef} className={css.tags}>
              <TagsGroup tags={tags} smallTags />
            </div>
          ) : null}

          <TextInput
            inputRef={ref}
            value={autocomplete.query}
            placeholder={props.readOnly ? undefined : placeholder}
            onChange={(v) => autocomplete.onQuery(v)}
            onKeyDown={autocomplete.onKeyDown}
            domRef={triggerRef}
            disabled={props.readOnly}
          />
        </div>
      </Field>
      {!props.disabled && !props.readOnly && (
        <Dropdown
          open={autocomplete.open && autocomplete.suggestions.length > 0}
          triggerRef={triggerRef}
          onOpen={() => autocomplete.onQuery(autocomplete.query)}
          onToggle={autocomplete.setOpen}
          anchor={anchor}
        >
          {loading || autocomplete.loading ? (
            <Text className={css.loading}>
              <Trans>Chargement des résultats...</Trans>
              <LoaderLine size="sm" style={{ marginLeft: "4px" }} />
            </Text>
          ) : (
            <List
              multiple
              controlRef={triggerRef}
              items={autocomplete.suggestions}
              selectedValues={value}
              onSelectValues={(values) => {
                ref.current?.focus()
                autocomplete.onSelect(values)
              }}
              normalize={normalize}
            >
              {children}
            </List>
          )}
        </Dropdown>
      )}
    </>
  )
}
