import { Button } from "common/components/button2"
import { FormManager } from "common/components/form2"
import { useQuery } from "common/hooks/async"
import { useMemo } from "react"
import { Trans, useTranslation } from "react-i18next"

type Page = "digestate" | "energy"

/**
 * Hook to get missing fields for a given page
 * Warning : useMissingFields is used in the common page header and we don't know the type of the form
 * @param form - The form manager
 * @returns The missing fields for the given page and a function to show the missing fields
 */
export const useMissingFields = <FormType extends object>(
  form: FormManager<FormType>
) => {
  const { t } = useTranslation()
  const { result } = useQuery(
    () =>
      Promise.resolve({
        digestate: [],
        energy: [],
      }),
    {
      key: "missing-fields-biomethane",
      params: [],
    }
  )
  const { setFieldError } = form

  const showMissingFields = (page: Page) => {
    result?.[page]?.forEach((field) => {
      setFieldError(field, t("Ce champ est obligatoire"))
    })
  }

  return { result, showMissingFields }
}

export const useMissingFieldsMessages = <FormType extends object>(
  form: FormManager<FormType>
) => {
  const { t } = useTranslation()
  const { result } = useMissingFields(form)
  const digestateCount = result?.digestate?.length ?? 0
  const energyCount = result?.energy?.length ?? 0

  const errorMessage = useMemo(() => {
    const pages: { page: string; count: number }[] = []
    const messages = [
      (page: string, count: number) => {
        const missingFieldsFirstMessage = t(
          "Champs manquants : il y a <strong>{{count}} champs manquants</strong> dans la section <CustomLink>{{page}}</CustomLink>",
          {
            count,
            page,
          }
        )
        return (
          <Trans
            defaults={missingFieldsFirstMessage}
            values={{ count, page }}
            components={{
              strong: <strong />,
              CustomLink: (
                // @ts-ignore children is propagated to the button by i18next
                <Button customPriority="link" linkProps={{ to: "" }} />
              ),
            }}
            key={page}
            t={t}
          />
        )
      },
      (page: string, count: number) => {
        const missingFieldsAdditionalMessage = t(
          " et <strong>{{count}} champs manquants</strong> dans la section <CustomLink>{{page}}</CustomLink>",
          {
            page,
            count,
          }
        )

        return (
          <Trans
            defaults={missingFieldsAdditionalMessage}
            values={{ count, page }}
            components={{
              strong: <strong />,
              CustomLink: (
                // @ts-ignore children is propagated to the button by i18next
                <Button customPriority="link" linkProps={{ to: "" }} />
              ),
            }}
            key={page}
            t={t}
          />
        )
      },
    ]
    if (digestateCount > 0)
      pages.push({ page: t("Digestat"), count: digestateCount })
    if (energyCount > 0) pages.push({ page: t("Energie"), count: energyCount })

    return pages.map(({ page, count }, index) => messages[index]?.(page, count))
  }, [digestateCount, energyCount, t])

  return { errorMessage, digestateCount, energyCount }
}
