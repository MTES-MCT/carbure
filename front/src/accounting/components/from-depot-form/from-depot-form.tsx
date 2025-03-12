import { useFormContext } from "common/components/form2"
import { Autocomplete } from "common/components/autocomplete2"
import { Trans, useTranslation } from "react-i18next"
import { Notice } from "common/components/notice"
import { getDepotsWithBalance } from "./api"
import useEntity from "common/hooks/entity"
import { Balance } from "accounting/types"
import { Grid } from "common/components/scaffold"
import { OperationText } from "accounting/components/operation-text"
import { useUnit } from "common/hooks/unit"
import { FromDepotFormProps } from "./from-depot-form.types"

// Type of the component
type FromDepotProps = {
  balance: Balance
}

export const FromDepotForm = ({ balance }: FromDepotProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { formatUnit } = useUnit()
  const { value, bind } = useFormContext<FromDepotFormProps>()

  return (
    <>
      <Autocomplete
        label={t("Sélectionnez un dépôt d'expédition")}
        placeholder={t("Rechercher un dépôt")}
        getOptions={(search) =>
          getDepotsWithBalance(entity.id, {
            sector: balance.sector,
            category: balance.customs_category,
            biofuel: balance.biofuel?.code ?? "",
            query: search,
          })
        }
        normalize={(depot) => ({
          label: depot.name,
          value: depot,
        })}
        required
        {...bind("from_depot")}
      >
        {({ data: depot }) => (
          <span>
            <Trans
              components={{ strong: <strong /> }}
              t={t}
              values={{
                depot: depot.name,
                quantity: formatUnit(depot.quantity.credit, 0),
              }}
              defaults="{{depot}} ({{quantity}} disponibles)"
            />
          </span>
        )}
      </Autocomplete>
      {value.from_depot && (
        <>
          {value.from_depot.quantity.credit &&
          value.from_depot.quantity.credit > 0 ? (
            <Notice noColor variant="info">
              <Trans
                components={{ strong: <strong /> }}
                t={t}
                values={{
                  depot: value.from_depot.name,
                  quantity: formatUnit(value.from_depot.quantity.credit, 0),
                }}
                defaults="Solde disponible dans le dépôt {{depot}} : <strong>{{quantity}}</strong>"
              />
            </Notice>
          ) : null}
          {value.from_depot.quantity.credit === 0 ? (
            <Notice noColor variant="warning">
              <Trans
                t={t}
                values={{ depot: value.from_depot.name }}
                defaults="Aucun solde disponible dans le dépôt {{depot}}"
              />
            </Notice>
          ) : null}
        </>
      )}
    </>
  )
}

// Recap form data after the step was submitted
export const FromDepotSummary = ({
  values,
}: {
  values: FromDepotFormProps
}) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit()
  if (
    !values.from_depot?.quantity?.credit ||
    values.from_depot.quantity.credit <= 0
  ) {
    return null
  }

  return (
    <Grid>
      <OperationText
        title={t("Dépôt d'expédition")}
        description={values.from_depot?.name ?? ""}
      />
      <OperationText
        title={t("Solde disponible dans le dépôt d'expédition")}
        description={formatUnit(values.from_depot.quantity.credit, 0)}
      />
    </Grid>
  )
}
