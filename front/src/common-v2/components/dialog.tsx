import cl from "clsx";
import { Cross } from "./icons";
import css from "./dialog.module.css";
import Portal from "./portal";
import Button from "./button";

export interface DialogProps {
  className?: string;
  style?: React.CSSProperties;
  children: React.ReactNode;
  onClose: () => void;
}

export const Dialog = ({
  className,
  style,
  children,
  onClose,
}: DialogProps) => (
  <Portal onClose={onClose}>
    <div className={css.screen}>
      <div className={css.overlay} onClick={onClose} />
      <div className={cl(css.dialog, className)} style={style}>
        {children}
        <Button
          variant="icon"
          icon={Cross}
          action={onClose}
          className={css.close}
        />
      </div>
    </div>
  </Portal>
);

export default Dialog;
