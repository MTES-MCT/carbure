/**
 * Shared helpers to build JSX messages with links for missing fields.
 * Used by declaration messages (digestat, énergie) and settings messages (contrat, production, injection).
 */
import { Trans } from "react-i18next"
import { Button } from "common/components/button2"
import { MISSING_FIELDS_HASH } from "./missing-fields.constants"

export const generateNoObjectMessage = (
  page: string,
  url: string,
  message: string,
  onPageClick?: (page: string) => void
) => {
  return (
    <span key={page}>
      <Trans
        defaults={message}
        components={{
          CustomLink: (
            // @ts-ignore children is propagated to the button by i18next
            <Button
              customPriority="link"
              linkProps={{
                to: url,
                onClick: () => onPageClick?.(page),
              }}
            />
          ),
        }}
      />
    </span>
  )
}

export const generateTranslatedMessage = (
  page: string,
  count: number,
  url: string,
  message: string,
  onPageClick?: (page: string) => void
) => {
  return (
    <span key={page}>
      <Trans
        defaults={message}
        values={{ count, page }}
        components={{
          strong: <strong />,
          CustomLink: (
            // @ts-ignore children is propagated to the button by i18next
            <Button
              customPriority="link"
              linkProps={{
                to: `${url}#${MISSING_FIELDS_HASH}`,
                onClick: () => onPageClick?.(page),
              }}
            />
          ),
        }}
        key={page}
        is="span"
      />
    </span>
  )
}
