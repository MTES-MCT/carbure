import { useMemo, useState } from "react"
import i18next from "i18next"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { DeclarationSummary, LotQuery } from "../types"
import { Normalizer } from "common/utils/normalize"
import useEntity from "common/hooks/entity"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation, useQuery } from "common/hooks/async"
import Portal from "common/components/portal"
import * as api from "../api"
import { LotSummary } from "../components/lots/lot-summary"
import { capitalize, formatDate, formatPeriod } from "common/utils/formatters"

import { Entity } from "common/types"
import { Row } from "common/components/scaffold"
import { useMatomo } from "matomo"
import { useHashMatch } from "common/components/hash-route"
import { Button } from "common/components/button2"
import { Select } from "common/components/selects2"
import { Dialog as Dialog2 } from "common/components/dialog2"
import { Notice } from "common/components/notice"

export const DeclarationButton = () => {
  const { t } = useTranslation()
  const location = useLocation()
  return (
    <Button
      asideX
      iconId="ri-draft-line"
      linkProps={{ to: { search: location.search, hash: "#declaration" } }}
    >
      {t("Gérer mes déclarations")}
    </Button>
  )
}

const now = new Date()
const currentPeriod = now.getFullYear() * 100 + now.getMonth() + 1 // add 1 so we're not 0 based for the months

export const DeclarationDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const notify = useNotify()
  const location = useLocation()
  const notifyError = useNotifyError()

  const matomo = useMatomo()
  const entity = useEntity()

  const years = useQuery(api.getYears, {
    key: "years",
    params: [entity.id],
  })

  const match = useHashMatch("declaration/:period")

  const initialPeriod = match?.params.period
    ? parseInt(match.params.period)
    : currentPeriod

  const initialMonth = initialPeriod % 100
  const initialYear = Math.floor(initialPeriod / 100)

  const [timeline, setTimeline] = useState({
    month: initialMonth,
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

    onError: (err) =>
      notifyError(err, t("La déclaration n'a pas pu être validée !")),
  })

  const invalidateDeclaration = useMutation(api.invalidateDeclaration, {
    invalidates: ["declarations"],

    onSuccess: () => {
      notify(t("La déclaration a bien été annulée !"), { variant: "success" })
    },

    onError: (err) =>
      notifyError(err, t("La déclaration n'a pas pu être annulée !")),
  })

  const yearsData = years.result?.data.data ?? [initialYear]
  const declarationsData = declarations.result?.data.data ?? []
  const declaration = declarationsData[timeline.month - 1] as DeclarationSummary | undefined // prettier-ignore
  const period = timeline.year * 100 + timeline.month

  // generate a special query to get the summary for this declaration
  const query = useDeclarationQuery({
    entity,
    year: timeline.year,
    period: period,
  })

  function prev() {
    if (timeline.month === 1) {
      setTimeline({ year: timeline.year - 1, month: 12 })
    } else {
      setTimeline({ ...timeline, month: timeline.month - 1 })
    }
  }

  function next() {
    if (timeline.month === 12) {
      setTimeline({ year: timeline.year + 1, month: 1 })
    } else {
      setTimeline({ ...timeline, month: timeline.month + 1 })
    }
  }

  const hasPending = declaration ? declaration.pending > 0 : false

  const hasPrev = timeline.month > 1 || yearsData.includes(timeline.year - 1)
  const hasNext = timeline.month < 12 || yearsData.includes(timeline.year + 1)

  function onClose() {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={onClose}>
      <Dialog2
        style={{ minWidth: "min(100%, 700px)" }}
        onClose={onClose}
        header={<Dialog2.Title>{t("Déclaration de durabilité")}</Dialog2.Title>}
        footer={
          <>
            {declaration && declaration.pending > 0 && (
              <Notice
                variant="warning"
                title={
                  <Trans
                    count={declaration.pending}
                    defaults="Encore <b>{{count}} lots</b> en attente de validation"
                  />
                }
                size="small"
              ></Notice>
            )}
            {declaration?.declaration?.declared ? (
              <Button
                iconId="ri-close-line"
                loading={invalidateDeclaration.loading}
                customPriority="danger"
                asideX
                onClick={() => {
                  matomo.push([
                    "trackEvent",
                    "declarations",
                    "invalidate-declaration",
                    declaration?.period,
                  ])
                  invalidateDeclaration.execute(entity.id, period)
                }}
              >
                {t("Annuler la déclaration")}
              </Button>
            ) : (
              <Button
                disabled={hasPending}
                loading={validateDeclaration.loading}
                iconId="ri-check-line"
                onClick={() => {
                  matomo.push([
                    "trackEvent",
                    "declarations",
                    "validate-declaration",
                    declaration?.period,
                  ])
                  validateDeclaration.execute(entity.id, period)
                }}
                asideX
              >
                {t("Valider la déclaration")}
              </Button>
            )}
          </>
        }
      >
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
        <section>
          <Row style={{ gap: "var(--spacing-s)" }}>
            <Button
              disabled={!hasPrev}
              iconId="ri-arrow-left-s-line"
              onClick={prev}
              title="Previous"
              priority="tertiary"
            />
            <Select
              loading={years.loading}
              placeholder={t("Choisissez une année")}
              value={timeline.year}
              onChange={(year = initialYear) =>
                setTimeline({ ...timeline, year })
              }
              options={yearsData}
              sort={(v) => -v.value}
              style={{ flex: 1 }}
            />
            <Select
              loading={declarations.loading}
              placeholder={t("Choisissez un mois")}
              value={period}
              onChange={(period = initialPeriod) =>
                setTimeline({ ...timeline, month: period % 100 })
              }
              options={declarationsData}
              normalize={normalizeDeclaration}
              style={{ flex: 2 }}
            />
            <Button
              disabled={!hasNext}
              iconId="ri-arrow-right-s-line"
              onClick={next}
              title="Next"
              priority="tertiary"
            />
          </Row>
        </section>
        {declaration && <LotSummary pending query={query} />}
      </Dialog2>
    </Portal>
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
  const date = formatPeriod(declaration.period) + "-01"
  const localized = formatDate(date, "MMMM") // prettier-ignore
  const extra = i18next.t("{{count}} lots", { count: declaration.lots })
  const ok = declaration.declaration?.declared ? " ✔" : ""

  return {
    value: declaration.period,
    label: `${capitalize(localized)} : ${extra}${ok}`,
  }
}
