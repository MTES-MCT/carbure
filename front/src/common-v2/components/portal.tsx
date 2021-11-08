import React, { useEffect, useRef } from "react";
import ReactDOM from "react-dom";

export interface PortalProps {
  children: React.ReactNode;
  onClose?: () => void;
}

export const Portal = ({ children, onClose }: PortalProps) => {
  const containerRef = useRef(document.createElement("div"));

  // add the container div to the document and remove it when not needed
  useEffect(() => {
    const portal = containerRef.current;
    (portal.dataset as any).portal = true;
    document.body.appendChild(portal);
    return () => portal.remove();
  }, []);

  // watch for interactions on the target to act as trigger
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      switch (e.key) {
        // when pressing escape close the portal if it's the last one opened
        case "Escape":
          if (isLastPortal(containerRef.current)) onClose?.();
          break;
      }
    }

    window.addEventListener("keydown", onKeyDown, true);
    return () => window.removeEventListener("keydown", onKeyDown, true);
  }, [onClose]);

  return ReactDOM.createPortal(children, containerRef.current);
};

export function isLastPortal(element: Element) {
  return element.matches("div[data-portal]:last-child");
}

export default Portal;
