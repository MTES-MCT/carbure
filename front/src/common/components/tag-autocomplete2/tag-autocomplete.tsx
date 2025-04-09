import { TextInput } from "../inputs2"
import { useLayoutEffect, useRef } from "react"
import { Tag } from "@codegouvfr/react-dsfr/Tag"
import css from "./tag-autocomplete.module.css"
import { Field } from "./field"
import { Dropdown, Trigger } from "../dropdown2"
import { InputProps } from "../inputs2/input"
import { defaultNormalizer, Normalizer, Sorter } from "common/utils/normalize"
import { defaultRenderer, List, Renderer } from "../list2"
import { useTagAutocomplete } from "./tag-autocomplete.hooks"
import { Text } from "../text"
import { Trans } from "react-i18next"
import { LoaderLine } from "../icon"

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
  useLayoutEffect(() => {
    if (tagsRef.current && ref.current) {
      ref.current.style.paddingLeft = `calc(var(--spacing-2w) + ${tagsRef.current.offsetWidth}px)`
    }
  }, [tagsRef])

  return (
    <>
      <Field {...props}>
        <div style={{ position: "relative" }}>
          <div className={css.tags} ref={tagsRef}>
            <Tag
              small
              dismissible
              nativeButtonProps={{
                onClick: () => console.log("clicked"),
              }}
            >
              element 1
            </Tag>
            <Tag small dismissible>
              element 2
            </Tag>
          </div>
          <TextInput
            inputRef={ref}
            value={autocomplete.query}
            placeholder={props.readOnly ? undefined : placeholder}
            onChange={(v) => autocomplete.onQuery(v)}
            onKeyDown={autocomplete.onKeyDown}
            domRef={triggerRef}
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
            <Text style={{ padding: "10px", textAlign: "center" }}>
              <Trans>Chargement des résultats...</Trans>
              <LoaderLine size="sm" style={{ marginLeft: "4px" }} />
            </Text>
          ) : (
            <List
              multiple
              controlRef={triggerRef}
              items={autocomplete.suggestions}
              selectedValues={value}
              onSelectValues={autocomplete.onSelect}
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
