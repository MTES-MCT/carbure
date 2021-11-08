import React, { useEffect, useRef, useState } from "react";
import { defaultNormalizer, Normalizer } from "../hooks/normalize";
import { filterOptions } from "./autocomplete";
import Checkbox from "./checkbox";
import Dropdown, { Trigger } from "./dropdown";
import { Control, Field } from "./input";
import List, { defaultRenderer, Renderer } from "./list";
import { TagGroup } from "./tag";

export interface TagAutocompleteProps<T> extends Control, Trigger {
  value: T[] | undefined;
  options: T[];
  onChange: (value: T[] | undefined) => void;
  onQuery?: (query: string) => Promise<T[] | void> | T[] | void;
  normalize?: Normalizer<T>;
  children?: Renderer<T>;
}

function TagAutocomplete<T>({
  placeholder,
  value,
  options,
  onChange,
  onQuery,
  anchor,
  normalize = defaultNormalizer,
  children = defaultRenderer,
  ...props
}: TagAutocompleteProps<T>) {
  const triggerRef = useRef<HTMLInputElement>(null);

  const autocomplete = useTagAutocomplete({
    value,
    options,
    onChange,
    onQuery,
    normalize,
  });

  return (
    <>
      <Field {...props} domRef={triggerRef}>
        <TagGroup
          variant="info"
          items={value}
          onDismiss={onChange}
          normalize={normalize}
        >
          <input
            readOnly={props.readOnly}
            disabled={props.disabled}
            placeholder={placeholder}
            value={autocomplete.query}
            onChange={(e) => autocomplete.onQuery(e.target.value)}
            onKeyDown={autocomplete.onKeyDown}
          />
        </TagGroup>
      </Field>

      <Dropdown
        open={autocomplete.open && options.length > 0}
        triggerRef={triggerRef}
        onOpen={() => autocomplete.onQuery(autocomplete.query)}
        onToggle={autocomplete.setOpen}
        anchor={anchor}
      >
        <List
          multiple
          controlRef={triggerRef}
          items={autocomplete.options}
          selectedItems={value}
          onSelectItems={autocomplete.onSelect}
          normalize={normalize}
        >
          {({ selected, label }) => (
            <Checkbox readOnly value={selected}>
              {label}
            </Checkbox>
          )}
        </List>
      </Dropdown>
    </>
  );
}

interface AutocompleteConfig<T> {
  value: T[] | undefined;
  options: T[];
  onChange: (value: T[] | undefined) => void;
  onQuery?: (query: string) => Promise<T[] | void> | T[] | void;
  normalize?: Normalizer<T>;
}

export function useTagAutocomplete<T>({
  value = [],
  options: controlledOptions,
  onChange,
  onQuery: controlledOnQuery,
  normalize = defaultNormalizer,
}: AutocompleteConfig<T>) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  const [options, setOptions] = useState(controlledOptions);
  useEffect(() => setOptions(controlledOptions), [controlledOptions]);

  async function onQuery(query: string | undefined = "") {
    setQuery(query);
    setOpen(true);
    controlledOnQuery?.(query);

    const matches = filterOptions(query, options, normalize);
    setOptions(matches);
  }

  function onSelect(items: T[] | undefined) {
    onQuery("");
    onChange(items);
  }

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Backspace" && query === "") {
      onChange(value.slice(0, -1));
    }
  }

  return { query, options, open, setOpen, onQuery, onSelect, onKeyDown };
}

export default TagAutocomplete;
