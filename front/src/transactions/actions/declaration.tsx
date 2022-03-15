import { useMemo, useState } from "react"
import i18next from "i18next"
import { Trans, useTranslation } from "react-i18next"
import { DeclarationSummary, LotQuery } from "../types"
import { Normalizer } from "common-v2/utils/normalize"
import useEntity from "carbure/hooks/entity"
import { useNotify } from "common-v2/components/notifications"
import { useMutation, useQuery } from "common-v2/hooks/async"
import { usePortal } from "common-v2/components/portal"
import * as api from "../api"
import Button from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import { LotSummary } from "../components/lots/lot-summary"
import Select from "common-v2/components/select"
import Alert from "common-v2/components/alert"
import {
  capitalize,
  formatDate,
  formatPeriod,
} from "common-v2/utils/formatters"
import {
  AlertCircle,
  Certificate,
  Check,
  ChevronLeft,
  ChevronRight,
  Cross,
  Return,
} from "common-v2/components/icons"
import { Entity } from "carbure/types"
import { Row } from "common-v2/components/scaffold"
import { useMatomo } from "matomo"

export interface DeclarationButtonProps {
  year: number
  years: number[]
}

export const DeclarationButton = ({ year, years }: DeclarationButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  return (
    <Button
      asideX
      variant="primary"
      icon={Certificate}
      label={t("Valider ma déclaration")}
      action={() =>
        portal((close) => (
          <DeclarationDialog year={year} years={years} onClose={close} />
        ))
      }
    />
  )
}

export interface DeclarationDialogProps {
  year: number
  years: number[]
  onClose: () => void
}

const now = new Date()
const currentMonth = now.getMonth()
const currentYear = now.getFullYear()

export const DeclarationDialog = ({
  year: initialYear,
  years,
  onClose,
}: DeclarationDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()
  const entity = useEntity()

  const [timeline, setTimeline] = useState({
    month: currentMonth,
    year: initialYear,
  })

  const declarations = useQuery(api.getDeclarations, {
    key: "declarations",
    params: [entity.id, timeline.year],
  })

  const validateDeclaration = useMutation(api.validateDeclaration, {
    invalidates: ["declarations"],

    onSuccess: () => {
      notify(t("La déclaration a bien été validée !"), { variant: "success" })
    },

    onError: () => {
      notify(t("La déclaration n'a pas pu être validée !"), {
        variant: "danger",
      })
    },
  })

  const invalidateDeclaration = useMutation(api.invalidateDeclaration, {
    invalidates: ["declarations"],

    onSuccess: () => {
      notify(t("La déclaration a bien été annulée !"), { variant: "success" })
    },

    onError: () => {
      notify(t("La déclaration n'a pas pu être annulée !"), {
        variant: "danger",
      })
    },
  })

  const declarationsData = declarations.result?.data.data ?? []
  const declaration = declarationsData[timeline.month] as DeclarationSummary | undefined
  const period = timeline.year * 100 + timeline.month + 1

  // generate a special query to get the summary for this declaration
  const query = useDeclarationQuery({
    entity,
    year: timeline.year,
    period: period,
  })

  function prev() {
    if (timeline.month === 0) {
      setTimeline({ year: timeline.year - 1, month: 11 })
    } else {
      setTimeline({ ...timeline, month: timeline.month - 1 })
    }
  }

  function next() {
    if (timeline.month === 11) {
      setTimeline({ year: timeline.year + 1, month: 0 })
    } else {
      setTimeline({ ...timeline, month: timeline.month + 1 })
    }
  }

  const hasPending = declaration ? declaration.pending > 0 : false

  const hasPrev = timeline.month > 0 || years.includes(timeline.year - 1)
  const hasNext = timeline.month < 11 || years.includes(timeline.year + 1)

  return (
    <Dialog style={{ width: "max(50vw, 960px)" }} onClose={onClose}>
      <header>
        <h1>{t("Déclaration de durabilité")}</h1>
      </header>

      <main>
        <section>
          <p>
            {t(
              "Les tableaux suivants vous montrent un récapitulatif de vos entrées et sorties pour la période sélectionnée."
            )}
          </p>
          <p>
            {t(
              "Afin d'être comptabilisés, les brouillons que vous avez créé pour cette période devront être envoyés avant la fin du mois suivant ladite période. Une fois la totalité de ces lots validée, vous pourrez vérifier ici l'état global de vos transactions et finalement procéder à la déclaration."
            )}
          </p>
        </section>
        <section>
          <Row style={{ gap: "var(--spacing-s)" }}>
            <Button disabled={!hasPrev} icon={ChevronLeft} action={prev} />
            <Select
              placeholder={t("Choisissez une année")}
              value={timeline.year}
              onChange={(year = currentYear) => setTimeline({ ...timeline, year })} // prettier-ignore
              options={years}
              sort={v => -v.value}
              style={{ flex: 1 }}
            />
            <Select
              loading={declarations.loading}
              placeholder={t("Choisissez un mois")}
              value={timeline.month}
              onChange={(month = currentMonth) => setTimeline({ ...timeline, month })} // prettier-ignore
              options={declarationsData}
              normalize={normalizeDeclaration}
              style={{ flex: 2 }}
            />
            <Button disabled={!hasNext} icon={ChevronRight} action={next} />
          </Row>
        </section>
        {declaration && <LotSummary pending query={query} />}
      </main>
      <footer>
        {declaration?.declaration?.declared ? (
          <Button
            icon={Cross}
            loading={invalidateDeclaration.loading}
            variant="warning"
            label={t("Annuler la déclaration")}
            action={() => {
              matomo.push([
                "trackEvent",
                "declarations",
                "invalidate-declaration",
                declaration?.period,
              ])
              invalidateDeclaration.execute(entity.id, period)
            }}
          />
        ) : (
          <Button
            disabled={hasPending}
            loading={validateDeclaration.loading}
            variant="primary"
            icon={Check}
            label={t("Valider la déclaration")}
            action={() => {
              matomo.push([
                "trackEvent",
                "declarations",
                "validate-declaration",
                declaration?.period,
              ])
              validateDeclaration.execute(entity.id, period)
            }}
          />
        )}
        {declaration && declaration.pending > 0 && (
          <Alert variant="warning" icon={AlertCircle}>
            <p>
              <Trans count={declaration.pending}>
                Encore <b>{{ count: declaration.pending }} lots</b> en attente
                de validation
              </Trans>
            </p>
          </Alert>
        )}
        <Button asideX icon={Return} label={t("Retour")} action={onClose} />
      </footer>
    </Dialog>
  )
}

interface DeclarationQueryState {
  entity: Entity
  year: number
  period: number
}

function useDeclarationQuery({ entity, year, period }: DeclarationQueryState) {
  return useMemo<LotQuery>(
    () => ({
      year,
      entity_id: entity.id,
      periods: [`${period}`],
      status: "DECLARATION",
      history: true,
    }),
    [entity.id, period, year]
  )
}

const normalizeDeclaration: Normalizer<DeclarationSummary, number> = (
  declaration
) => {
  const month = (declaration.period % 100) - 1
  const date = formatPeriod(declaration.period) + "-01"
  const localized = formatDate(date, { day: undefined, year: undefined, month: 'long' }) // prettier-ignore
  const extra = i18next.t("{{count}} lots", { count: declaration.lots })
  const ok = declaration.declaration?.declared ? " ✔" : ""
  return { value: month, label: `${capitalize(localized)} : ${extra}${ok}` }
}
