import { useMemo, useState } from "react"
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
import { formatPeriod } from "common-v2/utils/formatters"
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

export interface DeclarationButtonProps {
  year: number
}

export const DeclarationButton = ({ year }: DeclarationButtonProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  return (
    <Button
      asideX
      variant="primary"
      icon={Certificate}
      label={t("Valider ma déclaration")}
      action={() =>
        portal((close) => <DeclarationDialog year={year} onClose={close} />)
      }
    />
  )
}

export interface DeclarationDialogProps {
  year: number
  onClose: () => void
}

const now = new Date()
const currentPeriod = now.getFullYear() * 100 + now.getMonth()

export const DeclarationDialog = ({
  year,
  onClose,
}: DeclarationDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()

  const [declaration, setDeclaration] = useState<DeclarationSummary | undefined>() // prettier-ignore

  const declarations = useQuery(api.getDeclarations, {
    key: "declarations",
    params: [entity.id, year],

    // select the current period by default
    onSuccess: (res) => {
      const declarations = res.data.data ?? []
      if (declaration === undefined) {
        setDeclaration(declarations.find((d) => d.period === currentPeriod))
      } else {
        setDeclaration(declarations.find((d) => d.period === declaration.period)) // prettier-ignore
      }
    },
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
  const period = declaration?.period ?? currentPeriod

  // generate a special query to get the summary for this declaration
  const query = useDeclarationQuery({ entity, year, period })

  function prev() {
    const index = declarationsData.indexOf(declaration!)
    setDeclaration(declarationsData[Math.max(0, index - 1)])
  }

  function next() {
    const index = declarationsData.indexOf(declaration!)
    setDeclaration(declarationsData[Math.min(index + 1, 11)])
  }

  const hasLots = Boolean(declaration?.lots)
  const hasPending = Boolean(declaration?.pending)

  return (
    <Dialog limit onClose={onClose}>
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
          <Row>
            <Button icon={ChevronLeft} action={prev} />
            <Select
              loading={declarations.loading}
              placeholder={t("Choisissez une période")}
              value={declaration}
              onChange={setDeclaration}
              options={declarationsData}
              normalize={normalizeDeclaration}
              style={{ flex: 1, margin: "0 var(--spacing-s)" }}
            />
            <Button icon={ChevronRight} action={next} />
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
            action={() => invalidateDeclaration.execute(entity.id, period)}
          />
        ) : (
          <Button
            disabled={!hasLots || hasPending}
            loading={validateDeclaration.loading}
            variant="primary"
            icon={Check}
            label={t("Valider la déclaration")}
            action={() => validateDeclaration.execute(entity.id, period)}
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

const normalizeDeclaration: Normalizer<DeclarationSummary> = (declaration) => ({
  value: declaration,
  label: formatPeriod(declaration.period),
})
