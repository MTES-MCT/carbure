import { NumberInput, RadioGroup } from "common/components/inputs2"
import { SelectDsfr } from "common/components/selects2"
import { useTranslation } from "react-i18next"
import {
  useMutateContractInfos,
  useInstallationCategoryOptions,
  useTariffReferenceOptions,
} from "./contract-infos.hooks"
import { Grid } from "common/components/scaffold"
import { Autocomplete } from "common/components/autocomplete2"
import { useFormContext } from "common/components/form2"
import { DeepPartial } from "common/types"
import {
  getRediiThresholdLabel,
  isContractRedii,
  isTariffReference2011Or2020,
  isTariffReference2021Or2023,
} from "../../contract.utils"
import { getYesNoOptions } from "common/utils/normalizers"
import { Button } from "common/components/button2"
import {
  BiomethaneContract,
  BiomethaneContractPatchRequest,
} from "biomethane/pages/contract/types"
import { Notice } from "common/components/notice"
import { findBuyerBiomethaneEntities } from "biomethane/pages/contract/api"
import useEntity from "common/hooks/entity"
import { usePortal } from "common/components/portal"
import { RedIIDialog } from "./red-ii-dialog"
import { useAllowedToEdit } from "biomethane/hooks/use-allowed-to-edit"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useSectionsManager } from "common/providers/sections-manager.provider"

type ContractInfosForm = DeepPartial<BiomethaneContractPatchRequest>

const CONTRACT_INFOS_SECTION_ID = "contract-infos"

const extractValues = (contract?: ContractInfosForm) => {
  return {
    tariff_reference: contract?.tariff_reference,
    buyer: contract?.buyer,
    installation_category: contract?.installation_category,
    cmax: contract?.cmax,
    pap_contracted: contract?.pap_contracted,
    cmax_annualized: contract?.cmax_annualized,
    cmax_annualized_value: contract?.cmax_annualized_value,
  }
}

export const ContractInfos = ({
  contract,
}: {
  contract?: BiomethaneContract
}) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const allowedToEdit = useAllowedToEdit()
  const portal = usePortal()
  const { bind, value } = useFormContext<ContractInfosForm>()
  const tariffReferenceOptions = useTariffReferenceOptions()
  const installationCategoryOptions = useInstallationCategoryOptions()
  const { execute: updateContract, loading } = useMutateContractInfos(contract)
  const { setSectionExpanded, isSectionExpanded } = useSectionsManager()

  const isEditing = isSectionExpanded(CONTRACT_INFOS_SECTION_ID)

  const onSubmit = () => {
    const formData = extractValues(value)
    const update = (is_red_ii: boolean) => {
      updateContract({ ...formData, is_red_ii }).then(() => {
        setSectionExpanded(CONTRACT_INFOS_SECTION_ID, false)
      })
    }

    // Allow the biomethane producer to set/unset the RED II status if the cmax or pap_contracted
    // is lower than the threshold
    if (entity.is_red_ii && !isContractRedii(value)) {
      portal((close) => (
        <RedIIDialog
          onClose={close}
          onConfirm={update}
          tariffReference={value.tariff_reference}
        />
      ))
    } else {
      updateContract(formData).then(() => {
        setSectionExpanded(CONTRACT_INFOS_SECTION_ID, false)
      })
    }
  }

  return (
    <ManagedEditableCard
      sectionId={CONTRACT_INFOS_SECTION_ID}
      title={t("Caractéristiques du contrat d’achat à tarif réglementé")}
      onEdit={(editing) =>
        setSectionExpanded(CONTRACT_INFOS_SECTION_ID, editing)
      }
      readOnly={!allowedToEdit}
    >
      <ManagedEditableCard.Form onSubmit={onSubmit}>
        {isContractRedii(value) && (
          <Notice variant="info" icon="fr-icon-info-line">
            {isTariffReference2011Or2020(value.tariff_reference)
              ? t(
                  "Votre Capacité maximale de production contractualisée est strictement supérieure à {{value}}, votre production de biométhane est donc soumise aux exigences RED.",
                  {
                    value: getRediiThresholdLabel(value.tariff_reference),
                  }
                )
              : t(
                  "Votre production annuelle prévisionnelle est strictement supérieure à {{value}}, votre production de biométhane est donc soumise aux exigences RED.",
                  {
                    value: getRediiThresholdLabel(value.tariff_reference),
                  }
                )}
          </Notice>
        )}
        <Grid cols={2} gap="lg">
          <SelectDsfr
            label={t("Référence de l'arrêté tarifaire")}
            options={tariffReferenceOptions}
            required
            {...bind("tariff_reference")}
            readOnly={!isEditing}
          />
          <Autocomplete
            label={t("Acheteur")}
            getOptions={findBuyerBiomethaneEntities}
            normalize={(entity) => ({
              label: entity.name,
              value: entity.id,
            })}
            required
            {...bind("buyer")}
            readOnly={!isEditing}
          />
        </Grid>
        <SelectDsfr
          label={t("Catégorie d'installation")}
          options={installationCategoryOptions}
          required
          {...bind("installation_category")}
          readOnly={!isEditing}
        />

        {isTariffReference2011Or2020(value.tariff_reference) && (
          <>
            <Grid cols={2} gap="lg">
              <NumberInput
                label={t("Cmax (Nm³/h)")}
                min={0}
                {...bind("cmax")}
                required
                readOnly={!isEditing}
                hasTooltip
                title={t(
                  "Dernière capacité maximale de production contractualisée en vigueur"
                )}
              />
              <RadioGroup
                label={t("Annualisation du contrôle de la Cmax")}
                options={getYesNoOptions()}
                orientation="horizontal"
                required
                {...bind("cmax_annualized")}
                readOnly={!isEditing}
              />
            </Grid>

            {value.cmax_annualized && (
              <NumberInput
                label={t("Cmax annualisée (GWhPCS/an)")}
                min={0}
                required
                {...bind("cmax_annualized_value")}
                readOnly={!isEditing}
              />
            )}
          </>
        )}

        {isTariffReference2021Or2023(value.tariff_reference) && (
          <NumberInput
            label={t("PAP contractualisée (GWhPCS/an)")}
            min={0}
            {...bind("pap_contracted")}
            required
            readOnly={!isEditing}
            hasTooltip
            title={t(
              "Dernière capacité maximale de production contractualisée en vigueur"
            )}
          />
        )}
        {isEditing && (
          <Button type="submit" iconId="ri-save-line" asideX loading={loading}>
            {t("Sauvegarder")}
          </Button>
        )}
      </ManagedEditableCard.Form>
    </ManagedEditableCard>
  )
}
