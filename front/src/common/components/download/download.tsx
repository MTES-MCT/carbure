import {
  Download as DSFRDownload,
  DownloadProps as DSFRDownloadProps,
} from "@codegouvfr/react-dsfr/Download"
import cl from "clsx"
import styles from "./download.module.css"

type DownloadProps = Omit<DSFRDownloadProps, "details"> & {
  spacing?: boolean
  details?: DSFRDownloadProps["details"]
}
/**
 * Create a wrapper around the DSFR Download component to add a custom class, remove the padding and margin bottom by default
 * @param props
 * @returns
 */
export const Download = ({ spacing = false, ...props }: DownloadProps) => {
  return (
    <DSFRDownload
      {...props}
      details={props.details ?? ""}
      className={cl(
        styles.download,
        props.className,
        !spacing && styles["no-margin"],
        !spacing && !props.details && styles["no-padding"]
      )}
    />
  )
}
