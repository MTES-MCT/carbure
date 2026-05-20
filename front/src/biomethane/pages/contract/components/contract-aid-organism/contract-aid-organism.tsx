import {
  BiomethaneContract,
  BiomethaneContractPatchRequest,
  ComplementaryAidOrganisms,
} from "biomethane/pages/contract/types"
import { useTranslation } from "react-i18next"
import { getYesNoOptions } from "common/utils/normalizers"
import { CheckboxGroup, RadioGroup, TextInput } from "common/components/inputs2"
import { useFormContext } from "common/components/form2"
import { useContractAidOrganismOptions } from "./contract-aid-organism.hooks"
import { Button } from "common/components/button2"
import { useMutateContractInfos } from "../contract-infos/contract-infos.hooks"
import { useAllowedToEdit } from "biomethane/hooks/use-allowed-to-edit"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useBiomethaneBackendInputLabel } from "biomethane/hooks/use-biomethane-backend-input-label"

type ContractAidOrganismForm = Pick<
  BiomethaneContractPatchRequest,
  | "has_complementary_investment_aid"
  | "complementary_aid_organisms"
  | "complementary_aid_other_organism_name"
>

const extractValues = (contract?: ContractAidOrganismForm) => {
  return {
    has_complementary_investment_aid:
      contract?.has_complementary_investment_aid,
    complementary_aid_organisms: contract?.complementary_aid_organisms ?? [],
    complementary_aid_other_organism_name:
      contract?.complementary_aid_other_organism_name ?? "",
  }
}

export const ContractAidOrganism = ({
  contract,
}: {
  contract?: BiomethaneContract
}) => {
  const { t } = useTranslation()
  const tBiomethaneInput = useBiomethaneBackendInputLabel()
  const allowedToEdit = useAllowedToEdit()

  const { bind, value } = useFormContext<ContractAidOrganismForm>()
  const { mutate: updateContractAidOrganism, isPending: loading } =
    useMutateContractInfos(contract)

  const complementaryAidOrganismOptions = useContractAidOrganismOptions()

  const onSubmit = () => {
    updateContractAidOrganism(extractValues(value))
  }

  return (
    <ManagedEditableCard
      sectionId="contract-aid-organism"
      title={t("Aide complémentaire à l'investissement")}
      readOnly={!allowedToEdit}
    >
      {({ isEditing }) => (
        <ManagedEditableCard.Form onSubmit={onSubmit}>
          <RadioGroup
            readOnly={!isEditing}
            label={tBiomethaneInput(
              "contract.has_complementary_investment_aid"
            )}
            options={getYesNoOptions()}
            {...bind("has_complementary_investment_aid")}
            orientation="horizontal"
            required
          />
          {value.has_complementary_investment_aid && (
            <>
              <CheckboxGroup
                readOnly={!isEditing}
                label={tBiomethaneInput("contract.complementary_aid_organisms")}
                options={complementaryAidOrganismOptions}
                {...bind("complementary_aid_organisms")}
                value={value.complementary_aid_organisms ?? []}
                required
              />
              {value.complementary_aid_organisms?.includes(
                ComplementaryAidOrganisms.OTHER
              ) && (
                <TextInput
                  readOnly={!isEditing}
                  label={tBiomethaneInput(
                    "contract.complementary_aid_other_organism_name"
                  )}
                  {...bind("complementary_aid_other_organism_name")}
                  required
                />
              )}
            </>
          )}
          {isEditing && (
            <Button
              type="submit"
              iconId="ri-save-line"
              asideX
              loading={loading}
            >
              {t("Sauvegarder")}
            </Button>
          )}
        </ManagedEditableCard.Form>
      )}
    </ManagedEditableCard>
  )
}
