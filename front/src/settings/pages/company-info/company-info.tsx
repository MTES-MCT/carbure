import useEntity from "common/hooks/entity"
import { Country, Entity, UserRole } from "common/types"
import { useForm, Form } from "common/components/form2"
import { TextInput } from "common/components/inputs2"
import { Grid, LoaderOverlay } from "common/components/scaffold"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import * as api from "../../api/company"
import { CompanyFormValue, SearchCompanyPreview } from "companies/types"
import { Autocomplete } from "common/components/autocomplete2"
import { findCountries } from "common/api"
import { normalizeCountry } from "common/utils/normalizers"
import { usePortal } from "common/components/portal"
import CompanyInfoSirenDialog from "./company-info-siren-dialog"
import { EditableCard } from "common/molecules/editable-card"
import { Notice } from "common/components/notice"
import { Icon } from "common/components/icon"
import { Button } from "common/components/button2"
import { useState } from "react"

type CompanyInfoProps = {
  company?: Entity
  readOnly?: boolean
}

const CompanyInfo = ({
  company,
  readOnly: _readOnly = false,
}: CompanyInfoProps) => {
  const { t } = useTranslation()
  const loggedEntity = useEntity()
  const portal = usePortal()
  const [isEditingCompanyAddress, setIsEditingCompanyAddress] = useState(false)
  const entity = company || loggedEntity

  const isAllowedToEdit =
    !_readOnly &&
    (!company || loggedEntity.hasRights(UserRole.Admin, UserRole.ReadWrite))

  const updateEntity = useMutation(api.updateEntity, {
    invalidates: ["user-settings"],
  })
  const companyForm = useCompanyForm(entity)

  const canSave = hasChange(entity, companyForm.value)

  const onSubmitForm = async (formValue: CompanyFormValue | undefined) => {
    if (formValue && canSave) {
      await updateEntity.execute(
        entity.id,
        formValue.activity_description!,
        formValue.legal_name!,
        formValue.registered_address!,
        formValue.registered_city!,
        formValue.registered_country?.code_pays || "",
        formValue.registered_zipcode!,
        formValue.registration_id!,
        formValue.sustainability_officer_email!,
        formValue.sustainability_officer_phone_number!.trim(),
        formValue.sustainability_officer!,
        formValue.website!,
        formValue.vat_number!
      )
      setIsEditingCompanyAddress(false)
    }
  }

  const prefillCompanyInfo = (prefetchedCompany: SearchCompanyPreview) => {
    setIsEditingCompanyAddress(true)
    companyForm.setField("legal_name", prefetchedCompany.legal_name)
    companyForm.setField(
      "registered_address",
      prefetchedCompany.registered_address
    )
    companyForm.setField("registered_city", prefetchedCompany.registered_city)
    companyForm.setField(
      "registered_country",
      prefetchedCompany.registered_country
    )
    companyForm.setField(
      "registered_zipcode",
      prefetchedCompany.registered_zipcode
    )
    companyForm.setField("registration_id", prefetchedCompany.registration_id)
  }

  const showAutofillDialog = () => {
    portal((close) => (
      <CompanyInfoSirenDialog
        onClose={close}
        wantPrefillCompanyInfo={prefillCompanyInfo}
      />
    ))
  }

  const isLockedField =
    !companyForm.value.registered_country ||
    companyForm.value.registered_country.code_pays === "FR"

  return (
    <>
      <EditableCard
        title={t("Adresse de la société")}
        description={
          isAllowedToEdit
            ? t("Veuillez renseigner l'adresse de votre société.")
            : undefined
        }
        isEditing={isEditingCompanyAddress}
        onEdit={setIsEditingCompanyAddress}
        onCancel={() => {
          // Reset the form to the initial entity data
          companyForm.setValue(getCompanyDataFromEntity(entity))
        }}
      >
        {isAllowedToEdit && (
          <Notice
            variant={companyForm.value.registration_id ? "info" : "warning"}
            icon="ri-error-warning-line"
            onAction={showAutofillDialog}
            linkText={
              <span>
                {t("Compléter mes informations")}
                <Icon
                  name="ri-search-line"
                  style={{ marginLeft: "4px" }}
                  size="sm"
                />
              </span>
            }
          >
            {t("Complétez vos informations à partir de votre numéro SIREN")}
          </Notice>
        )}

        <Form form={companyForm} onSubmit={onSubmitForm}>
          <Grid cols={2} gap="lg">
            <Autocomplete
              required
              readOnly={!isAllowedToEdit || !isEditingCompanyAddress}
              label={t("Pays")}
              placeholder={t("Rechercher un pays...")}
              getOptions={findCountries}
              normalize={normalizeCountry}
              {...companyForm.bind("registered_country")}
            />

            <TextInput
              required
              readOnly={!isAllowedToEdit || !isEditingCompanyAddress}
              label={t(
                "N° d'enregistrement de la société (SIREN ou équivalent)"
              )}
              {...companyForm.bind("registration_id")}
              disabled={isLockedField}
            />

            <TextInput
              required
              readOnly={!isAllowedToEdit || !isEditingCompanyAddress}
              label={t("Nom légal")}
              {...companyForm.bind("legal_name")}
              disabled={isLockedField}
            />
            <TextInput
              required
              readOnly={!isAllowedToEdit || !isEditingCompanyAddress}
              label={t("Adresse de la société (Numéro et rue)")}
              {...companyForm.bind("registered_address")}
              disabled={isLockedField}
            />
            <TextInput
              required
              readOnly={!isAllowedToEdit || !isEditingCompanyAddress}
              label={t("Ville")}
              {...companyForm.bind("registered_city")}
              disabled={isLockedField}
            />
            <TextInput
              required
              readOnly={!isAllowedToEdit || !isEditingCompanyAddress}
              label={t("Code postal")}
              {...companyForm.bind("registered_zipcode")}
              disabled={isLockedField}
            />
          </Grid>
          {isAllowedToEdit && isEditingCompanyAddress && (
            <Button
              asideX
              type="submit"
              disabled={!canSave}
              iconId="ri-save-line"
            >
              {t("Sauvegarder")}
            </Button>
          )}
        </Form>

        {updateEntity.loading && <LoaderOverlay />}
      </EditableCard>
      <EditableCard
        title={t("Coordonnées du contact principal")}
        onCancel={() => {
          // Reset the form to the initial entity data
          companyForm.setValue(getCompanyDataFromEntity(entity))
        }}
      >
        {({ isEditing }) => (
          <EditableCard.Form form={companyForm} onSubmit={onSubmitForm}>
            <Grid cols={2} gap="lg">
              <TextInput
                required
                readOnly={!isAllowedToEdit || !isEditing}
                label={t("Contact principal")}
                placeholder="Jean-Pierre Champollion"
                {...companyForm.bind("sustainability_officer")}
              />
              <TextInput
                readOnly={!isAllowedToEdit || !isEditing}
                placeholder="https://www.example.com"
                type="url"
                label={t("Site web (https://...)")}
                {...companyForm.bind("website")}
              />
              <TextInput
                required
                type="tel"
                pattern="^\+[0-9]{1,3}\s?[0-9]{6,14}$"
                label={t(
                  "N° téléphone contact principal (commence par +33 pour la France)"
                )}
                placeholder="exemple : +33612345678"
                readOnly={!isAllowedToEdit || !isEditing}
                {...companyForm.bind("sustainability_officer_phone_number")}
              />
              <TextInput
                readOnly={!isAllowedToEdit || !isEditing}
                label={t("Numéro de TVA")}
                {...companyForm.bind("vat_number")}
              />
            </Grid>
            <TextInput
              required
              type="email"
              readOnly={!isAllowedToEdit || !isEditing}
              label={t("Email contact principal")}
              {...companyForm.bind("sustainability_officer_email")}
            />
            {/* <TextArea
           required
           maxLength={5000}
           readOnly={!isAllowedToEdit}
           label={t("Description de l'activité")}
           {...companyForm.bind("activity_description")}
         /> */}
            {isAllowedToEdit && isEditing && (
              <Button
                asideX
                type="submit"
                disabled={!canSave}
                iconId="ri-save-line"
              >
                {t("Sauvegarder")}
              </Button>
            )}
          </EditableCard.Form>
        )}
      </EditableCard>
    </>
  )
}

export default CompanyInfo

function hasChange(entity: Entity, formEntity: CompanyFormValue) {
  return (
    entity.name !== formEntity.name ||
    entity.legal_name !== formEntity.legal_name ||
    entity.registration_id !== formEntity.registration_id ||
    entity.sustainability_officer !== formEntity.sustainability_officer ||
    entity.sustainability_officer_phone_number !==
      formEntity.sustainability_officer_phone_number ||
    entity.sustainability_officer_email !==
      formEntity.sustainability_officer_email ||
    entity.registered_address !== formEntity.registered_address ||
    entity.registered_city !== formEntity.registered_city ||
    entity.registered_zipcode !== formEntity.registered_zipcode ||
    entity.registered_country !== formEntity.registered_country ||
    entity.activity_description !== formEntity.activity_description ||
    entity.website !== formEntity.website ||
    entity.vat_number !== formEntity.vat_number
  )
}

const useCompanyForm = (entity: Entity) => {
  return useForm(getCompanyDataFromEntity(entity))
}

const getCompanyDataFromEntity = (entity: Entity) => ({
  activity_description: entity?.activity_description as string | undefined,
  name: entity?.name as string | undefined,
  legal_name: entity?.legal_name as string | undefined,
  registered_address: entity?.registered_address as string | undefined,
  registered_city: entity?.registered_city as string | undefined,
  registered_country: entity?.registered_country as Country | undefined,
  registered_zipcode: entity?.registered_zipcode as string | undefined,
  registration_id: entity?.registration_id as string | undefined,
  sustainability_officer_email: entity?.sustainability_officer_email as
    | string
    | undefined,
  sustainability_officer_phone_number:
    entity?.sustainability_officer_phone_number as string | undefined,
  sustainability_officer: entity?.sustainability_officer as string | undefined,
  website: entity?.website as string | undefined,
  vat_number: entity?.vat_number as string | undefined,
})
