import cl from "clsx";
import {
  defaultNormalizer,
  Normalizer,
  normalizeTree,
} from "../hooks/normalize";
import { multipleSelection } from "../hooks/selection";
import Button from "./button";
import { Cross } from "./icons";
import css from "./tag.module.css";

export type TagVariant = "info" | "success" | "warning" | "danger";

export interface TagProps {
  big?: boolean;
  variant?: TagVariant;
  label?: string;
  children?: React.ReactNode;
  onDismiss?: () => void;
}

export const Tag = ({ big, variant, label, children, onDismiss }: TagProps) => (
  <span className={cl(css.tag, variant && css[variant], big && css.big)}>
    {label ?? children}
    {onDismiss && (
      <Button captive variant="icon" icon={Cross} action={onDismiss} />
    )}
  </span>
);

export interface TagGroupProps<T> {
  children?: React.ReactNode;
  variant?: TagVariant;
  items: T[] | undefined;
  onDismiss?: (items: T[]) => void;
  normalize?: Normalizer<T>;
}

export function TagGroup<T>({
  children,
  variant,
  items,
  onDismiss,
  normalize = defaultNormalizer,
}: TagGroupProps<T>) {
  const normItems = normalizeTree(items ?? [], normalize);
  const { onSelect } = multipleSelection(items, onDismiss, normalize);

  return (
    <div className={css.group}>
      {normItems.map((item) => (
        <Tag
          key={item.key}
          variant={variant}
          label={item.label}
          onDismiss={onDismiss ? () => onSelect(item.value) : undefined}
        />
      ))}
      {children}
    </div>
  );
}

export default Tag;
