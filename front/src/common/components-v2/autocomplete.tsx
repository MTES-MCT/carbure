import { useEffect, useRef, useState } from "react";
import {
  defaultNormalizer,
  Filter,
  Normalizer,
  normalizeTree,
} from "../hooks/normalize";
import Dropdown, { Trigger } from "./dropdown";
import { Control, TextInput } from "./input";
import List, { defaultRenderer, Renderer } from "./list";

export interface AutocompleteProps<T> extends Control, Trigger {
  value: T | undefined;
  options: T[];
  onChange: (value: T | undefined) => void;
  onQuery?: (query: string) => Promise<T[] | void> | T[] | void;
  normalize?: Normalizer<T>;
  children?: Renderer<T>;
}

function Autocomplete<T>({
  value,
  options,
  onChange,
  onQuery,
  anchor,
  normalize = defaultNormalizer,
  children = defaultRenderer,
  ...props
}: AutocompleteProps<T>) {
  const triggerRef = useRef<HTMLInputElement>(null);

  const autocomplete = useAutocomplete({
    value,
    options,
    onChange,
    onQuery,
    normalize,
  });

  return (
    <>
      <TextInput
        {...props}
        domRef={triggerRef}
        value={autocomplete.query}
        onChange={autocomplete.onQuery}
      />

      <Dropdown
        open={autocomplete.open && options.length > 0}
        triggerRef={triggerRef}
        onOpen={() => autocomplete.onQuery(autocomplete.query)}
        onToggle={autocomplete.setOpen}
        anchor={anchor}
      >
        <List
          controlRef={triggerRef}
          items={autocomplete.options}
          selectedItem={value}
          children={children}
          normalize={normalize}
          onFocus={onChange}
          onSelectItem={autocomplete.onSelect}
        />
      </Dropdown>
    </>
  );
}

interface AutocompleteConfig<T> {
  value: T | undefined;
  options: T[];
  onChange: (value: T | undefined) => void;
  onQuery?: (query: string) => Promise<T[] | void> | T[] | void;
  normalize?: Normalizer<T>;
}

export function useAutocomplete<T>({
  value,
  options: controlledOptions,
  onChange,
  onQuery: controlledOnQuery,
  normalize = defaultNormalizer,
}: AutocompleteConfig<T>) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  const label = value ? normalize(value).label : "";
  useEffect(() => setQuery(label), [label]);

  const [options, setOptions] = useState(controlledOptions);
  useEffect(() => setOptions(controlledOptions), [controlledOptions]);

  function matchQuery(query: string, options: T[]) {
    const key = value ? normalize(value).key : "";
    const match = options.find((item) => normalize(item).label === query);
    if (match && normalize(match).key !== key) onChange(match);
  }

  async function onQuery(query: string | undefined) {
    setQuery(query ?? "");

    // reset autocomplete value if query is emptied
    if (!query) onChange(undefined);

    // stop here if we just cleared the input
    if (query === undefined) return;
    // and open the dropdown otherwise
    else setOpen(true);

    const matches = filterOptions(query, controlledOptions, normalize);

    setOptions(matches);
    matchQuery(query, matches);

    if (controlledOnQuery) {
      const nextOptions = await controlledOnQuery(query);
      if (nextOptions) matchQuery(query, nextOptions);
    }
  }

  function onSelect(value: T | undefined) {
    onChange(value);
    setOpen(false);

    // filter options based on the selected value label
    const query = value ? normalize(value).label : "";
    const matches = filterOptions(query, controlledOptions, normalize);
    setOptions(matches);
  }

  return { query, options, open, setOpen, onQuery, onSelect };
}

export function filterOptions<T>(
  query: string,
  options: T[],
  normalize: Normalizer<T>
) {
  const filter: Filter<T> = (item) => item.label.includes(query);
  return normalizeTree(options, normalize, filter).map((o) => o.value);
}

export default Autocomplete;
