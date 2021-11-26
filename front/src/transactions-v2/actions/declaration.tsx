import { useMemo, useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { DeclarationSummary, LotQuery } from "../types"
import { Normalizer } from "common-v2/utils/normalize"
import useEntity from "carbure/hooks/entity"
import { useQuery } from "common-v2/hooks/async"
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
  Return,
} from "common-v2/components/icons"
import { Entity } from "carbure/types"

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
const currentPeriod = `${now.getFullYear() * 100 + now.getMonth()}`

export const DeclarationDialog = ({
  year,
  onClose,
}: DeclarationDialogProps) => {
  const { t } = useTranslation()
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
      }
    },
  })

  const declarationsData = declarations.result?.data.data
  const period = declaration?.period ?? currentPeriod

  // generate a special query to get the summary for this declaration
  const query = useDeclarationQuery({ entity, year, period })

  return (
    <Dialog limit onClose={onClose}>
      <header>
        <h1>{t("Gestion des déclarations")}</h1>
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
              "Afin d'être comptabilisés, les brouillons que vous avez créé pour cette période devront être envoyés avant la fin du mois suivant ladite période. Une fois la totalité de ces lots validés, vous pourrez vérifier ici l'état global de vos transactions et finalement procéder à la déclaration."
            )}
          </p>
        </section>
        <section>
          <Select
            loading={declarations.loading}
            label={t("Période de déclaration")}
            placeholder={t("Choisissez une période")}
            value={declaration}
            onChange={setDeclaration}
            options={declarationsData}
            normalize={normalizeDeclaration}
          />
        </section>
        {declaration && <LotSummary pending query={query} />}
      </main>
      <footer>
        {declaration?.declaration?.declared ? (
          <Button
            disabled
            icon={Check}
            variant="success"
            label={t("Déclaration validée")}
          />
        ) : (
          <Button
            disabled={Boolean(declaration?.pending)}
            variant="primary"
            icon={Check}
            label={t("Valider la déclaration")}
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
  period: string
}

function useDeclarationQuery({ entity, year, period }: DeclarationQueryState) {
  return useMemo<LotQuery>(
    () => ({
      year,
      entity_id: entity.id,
      periods: [period],
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
