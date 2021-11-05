import React, { useCallback, useState } from "react";
import ReactDOM from "react-dom";
import cl from "clsx";
import { Cross } from "./icons";
import css from "./notifications.module.css";
import Button from "./button";

// initialize notification container and add it to the dom
const container = document.createElement("ul");
container.id = "notifications";
document.body.append(container);

export type NotificationsProps = {
  list: Notification[];
};

export const Notifications = ({ list }: NotificationsProps) => {
  if (list.length === 0) {
    return null;
  }

  return ReactDOM.createPortal(
    <>
      {list.map(({ key, content, options, clear }, i) => (
        <li
          key={i}
          onClick={() => clearTimeout(key)}
          className={cl(
            css.notification,
            options?.variant && css[options.variant]
          )}
        >
          <span className={css.content}>{content}</span>
          <Button
            variant="icon"
            icon={Cross}
            action={clear}
            className={css.close}
          />
        </li>
      ))}
    </>,
    container
  );
};

export const DEFAULT_TIMEOUT = 10000;

export type NotificationVariant = "info" | "success" | "warning" | "danger";

export interface NotificationOptions {
  variant?: NotificationVariant;
  timeout?: number;
}

export interface Notification {
  key: number;
  content: React.ReactNode;
  options?: NotificationOptions;
  clear: () => void;
}

export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const notify = useCallback(
    (content: React.ReactNode, options?: NotificationOptions) => {
      function clear() {
        setNotifications((list) => list.filter((n) => n.key !== key));
      }

      // set auto close with timeout
      const key = window.setTimeout(clear, options?.timeout ?? DEFAULT_TIMEOUT);

      const notification = { key, content, options, clear };
      setNotifications((list) => [...list, notification]);

      return notification;
    },
    []
  );

  const clear = useCallback((key: number) => {
    setNotifications((list) => {
      const notification = list.find((n) => n.key === key);

      if (notification) {
        notification.key && clearTimeout(notification.key);
        return list.filter((n) => n.key !== key);
      }

      return list;
    });
  }, []);

  return { notifications, notify, clear };
}
