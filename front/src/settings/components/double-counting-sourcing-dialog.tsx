import { findCountries, findFeedstocks } from "carbure/api"
import { Entity } from "carbure/types"
import { normalizeCountry, normalizeFeedstock } from "carbure/utils/normalizers"
import AutoComplete from "common/components/autocomplete"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Form, useForm } from "common/components/form"
import { Plus, Return, Save } from "common/components/icons"
import { NumberInput } from "common/components/input"
import { useMutation } from "common/hooks/async"
import { compact } from "common/utils/collection"
import { DoubleCountingSourcing } from "double-counting/types"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api/double-counting"

type DoubleCountingSourcingDialogProps = {
  add?: boolean
  dcaID: number
  sourcing?: DoubleCountingSourcing
  entity: Entity
  onClose: () => void
}

const DoubleCountingSourcingDialog = ({
  add,
  dcaID,
  sourcing,
  entity,
  onClose,
}: DoubleCountingSourcingDialogProps) => {
  const { t } = useTranslation()

  const { value, bind } = useForm<Partial<DoubleCountingSourcing>>(
    sourcing ?? {
      year: new Date().getFullYear(),
      feedstock: undefined,
      metric_tonnes: 0,
      origin_country: undefined,
      transit_country: undefined,
      supply_country: undefined,
    }
  )

  const addSourcing = useMutation(api.addDoubleCountingSourcing, {
    invalidates: ["dc-application-details"],
    onSuccess: () => onClose(),
  })

  const updateSourcing = useMutation(api.updateDoubleCountingSourcing, {
    invalidates: ["dc-application-details"],
  })

  async function saveSourcing() {
    if (
      !value.year ||
      !value.metric_tonnes ||
      !value.feedstock ||
      !value.origin_country ||
      !value.transit_country ||
      !value.supply_country
    ) {
      return
    }

    if (add) {
      await addSourcing.execute(
        entity.id,
        dcaID,
        value.year,
        value.metric_tonnes,
        value.feedstock.code,
        value.origin_country.code_pays,
        value.transit_country.code_pays,
        value.supply_country.code_pays
      )
    } else if (sourcing) {
      await updateSourcing.execute(entity.id, sourcing.id, value.metric_tonnes)
    }
  }

  const disabled =
    !value.year ||
    !value.metric_tonnes ||
    !value.feedstock ||
    !value.origin_country ||
    !value.transit_country ||
    !value.supply_country

  const loading = addSourcing.loading || updateSourcing.loading

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Approvisionnement")} </h1>
      </header>

      <main>
        <section>
          <p>
            {t(
              "Précisez les informations concernant votre approvisionnement en matière première dans le formularie ci-dessous."
            )}
          </p>
        </section>

        <section>
          <Form id="sourcing" onSubmit={saveSourcing}>
            <NumberInput
              autoFocus
              label={t("Année")}
              {...bind("year")}
              disabled={!add}
            />
            <AutoComplete
              label={t("Matière première")}
              normalize={normalizeFeedstock}
              getOptions={(search) => findFeedstocks(search, true)}
              defaultOptions={compact([value.feedstock])}
              {...bind("feedstock")}
              disabled={!add}
            />
            <NumberInput
              label={t("Poids en tonnes")}
              type="number"
              {...bind("metric_tonnes")}
            />
            <AutoComplete
              label={t("Pays d'origine")}
              getOptions={findCountries}
              defaultOptions={compact([value.origin_country])}
              normalize={normalizeCountry}
              {...bind("origin_country")}
              disabled={!add}
            />
            <AutoComplete
              label={t("Pays de transit")}
              getOptions={findCountries}
              defaultOptions={compact([value.transit_country])}
              normalize={normalizeCountry}
              {...bind("transit_country")}
              disabled={!add}
            />
            <AutoComplete
              label={t("Pays d'approvisionnement")}
              getOptions={findCountries}
              defaultOptions={compact([value.supply_country])}
              normalize={normalizeCountry}
              {...bind("supply_country")}
              disabled={!add}
            />
          </Form>
        </section>
      </main>

      <footer>
        <Button
          asideX
          disabled={disabled}
          submit="sourcing"
          variant="primary"
          loading={loading}
          icon={add ? Plus : Save}
        >
          {add ? (
            <Trans>Ajouter un approvisionnement</Trans>
          ) : (
            <Trans>Enregistrer les modifications</Trans>
          )}
        </Button>
        <Button icon={Return} action={onClose} label={t("Annuler")} />
      </footer>
    </Dialog>
  )
}

export default DoubleCountingSourcingDialog
