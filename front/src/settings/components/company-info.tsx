import useEntity from "carbure/hooks/entity"
import { Country, Entity, UserRole } from "carbure/types"
import Button from "common/components/button"
import Form, { useForm } from "common/components/form"
import { AlertCircle, Save, Search } from "common/components/icons"
import { TextArea, TextInput } from "common/components/input"
import { LoaderOverlay, Panel } from "common/components/scaffold"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import * as api from "../api/company"
import { CompanyFormValue, SearchCompanyPreview } from "companies/types"
import Autocomplete from "common/components/autocomplete"
import { findCountries } from "carbure/api"
import { normalizeCountry } from "carbure/utils/normalizers"
import Alert from "common/components/alert"
import { usePortal } from "common/components/portal"
import CompanyInfoSirenDialog from "./company-info-siren-dialog"


type CompanyInfoProps = {
  company?: Entity
}

const CompanyInfo = ({ company }: CompanyInfoProps) => {
  const { t } = useTranslation()
  const loggedEntity = useEntity()
  const portal = usePortal()

  const entity = company || loggedEntity
  const readOnly = company && !loggedEntity.hasRights(UserRole.Admin, UserRole.ReadWrite)

  const updateEntity = useMutation(api.updateEntity, {
    invalidates: ["user-settings"],
  })
  const companyForm = useCompanyForm(entity)

  const canSave = hasChange(entity, companyForm.value)

  const onSubmitForm = (formValue: CompanyFormValue | undefined) => {
    if (formValue && canSave) {
      updateEntity.execute(
        entity.id,
        formValue.activity_description!,
        formValue.legal_name!,
        formValue.registered_address!,
        formValue.registered_city!,
        formValue.registered_country?.code_pays!,
        formValue.registered_zipcode!,
        formValue.registration_id!,
        formValue.sustainability_officer_email!,
        formValue.sustainability_officer_phone_number!.trim(),
        formValue.sustainability_officer!,
        formValue.website!,
        formValue.vat_number!
      )
    }
  }

  const prefillCompanyInfo = (prefetchedCompany: SearchCompanyPreview) => {
    companyForm.setField("legal_name", prefetchedCompany.legal_name)
    companyForm.setField("registered_address", prefetchedCompany.registered_address)
    companyForm.setField("registered_city", prefetchedCompany.registered_city)
    companyForm.setField("registered_country", prefetchedCompany.registered_country)
    companyForm.setField("registered_zipcode", prefetchedCompany.registered_zipcode)
    companyForm.setField("registration_id", prefetchedCompany.registration_id)
  }

  const showAutofillDialog = () => {
    portal((close) => (
      <CompanyInfoSirenDialog onClose={close} wantPrefillCompanyInfo={prefillCompanyInfo} />
    ))
  }

  const isLockedField = !companyForm.value.registered_country || companyForm.value.registered_country.code_pays === "FR"

  return (
    <Panel id="info">
      <header>
        <h1>{t("Informations sur la société")}</h1>
        {!readOnly && (
          <Button
            asideX
            submit="entity-info"
            disabled={!canSave}
            icon={Save}
            variant="primary"
            label={t("Enregistrer les modifications")}
          />
        )}
      </header>

      {!readOnly && (
        <section>
          <p>
            {t(
              "Veuillez renseigner les informations de contact de votre société."
            )}
          </p>
        </section>
      )}

      <section>
        <Alert icon={AlertCircle} variant={companyForm.value.registration_id ? "info" : "warning"}>
          {t(
            "Complétez vos données à partir de votre numéro SIREN"
          )}
          <Button variant="primary" action={showAutofillDialog} asideX         >
            {t("Compléter mes données")}
          </Button>
        </Alert>
      </section>

      <section>
        <Form
          form={companyForm}
          id="entity-info"
          onSubmit={onSubmitForm}
        >
          <Autocomplete
            required
            readOnly={readOnly}
            label={t("Pays")}
            placeholder={t("Rechercher un pays...")}
            getOptions={findCountries}
            normalize={normalizeCountry}
            {...companyForm.bind("registered_country")}
          />

          <TextInput
            required
            readOnly={readOnly}
            label={t("N° d'enregistrement de la société (SIREN ou équivalent)")}
            {...companyForm.bind("registration_id")}
            disabled={isLockedField}
          />

          <TextInput
            required
            readOnly={readOnly}
            label={t("Nom légal")}
            {...companyForm.bind("legal_name")}
            disabled={isLockedField}

          />
          <TextInput
            required
            readOnly={readOnly}
            label={t("Adresse de la société (Numéro et rue)")}
            {...companyForm.bind("registered_address")}
            disabled={isLockedField}

          />
          <TextInput
            required
            readOnly={readOnly}
            label={t("Ville")}
            {...companyForm.bind("registered_city")}
            disabled={isLockedField}

          />
          <TextInput
            required
            readOnly={readOnly}
            label={t("Code postal")}
            {...companyForm.bind("registered_zipcode")}
            disabled={isLockedField}

          />

          <TextInput
            required
            readOnly={readOnly}
            label={t("Responsable durabilité")}
            placeholder="Jean-Pierre Champollion"
            {...companyForm.bind("sustainability_officer")}
          />
          <TextInput
            required
            type="tel"
            pattern="^\+[0-9]{1,3}\s?[0-9]{6,14}$"
            label={t("N° téléphone responsable durabilité (commence par +33 pour la France)")}
            placeholder="exemple : +33612345678"
            readOnly={readOnly}
            {...companyForm.bind("sustainability_officer_phone_number")}
          />
          <TextInput
            required
            type="email"
            readOnly={readOnly}
            label={t("Email responsable durabilité")}
            {...companyForm.bind("sustainability_officer_email")}
          />

          <TextArea
            required
            maxLength={5000}
            readOnly={readOnly}
            label={t("Description de l'activité")}
            {...companyForm.bind("activity_description")}
          />

          <TextInput
            readOnly={readOnly}
            placeholder="https://www.example.com"
            type="url"
            label={t("Site web (https://...)")}
            {...companyForm.bind("website")}
          />

          <TextInput
            readOnly={readOnly}
            label={t("Numéro de TVA")}
            {...companyForm.bind("vat_number")}
          />
        </Form>
      </section>

      <footer />

      {updateEntity.loading && <LoaderOverlay />}
    </Panel>
  )
}


export default CompanyInfo


function hasChange(entity: Entity, formEntity: CompanyFormValue) {
  return (
    entity.name !== formEntity.name ||
    entity.legal_name !== formEntity.legal_name ||
    entity.registration_id !== formEntity.registration_id ||
    entity.sustainability_officer !== formEntity.sustainability_officer ||
    entity.sustainability_officer_phone_number !== formEntity.sustainability_officer_phone_number ||
    entity.sustainability_officer_email !== formEntity.sustainability_officer_email ||
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
  return useForm({
    activity_description: entity?.activity_description as string | undefined,
    name: entity?.name as string | undefined,
    legal_name: entity?.legal_name as string | undefined,
    registered_address: entity?.registered_address as string | undefined,
    registered_city: entity?.registered_city as string | undefined,
    registered_country: entity?.registered_country as Country | undefined,
    registered_zipcode: entity?.registered_zipcode as string | undefined,
    registration_id: entity?.registration_id as string | undefined,
    sustainability_officer_email: entity?.sustainability_officer_email as string | undefined,
    sustainability_officer_phone_number: entity?.sustainability_officer_phone_number as string | undefined,
    sustainability_officer: entity?.sustainability_officer as string | undefined,
    website: entity?.website as string | undefined,
    vat_number: entity?.vat_number as string | undefined,
  })
}
