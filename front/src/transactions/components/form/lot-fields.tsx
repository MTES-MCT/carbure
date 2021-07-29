import { Trans, useTranslation } from "react-i18next"
import { FormGroup } from "common/components/form"
import * as Fields from "./fields"
import { FieldsProps } from "./fields"
import { EntityType } from "common/types"
import { Link } from "common/components/relative-route"
import styles from "./fields.module.css"

export const LotFields = ({
  readOnly,
  data,
  entity,
  errors,
  editable,
  onChange,
}: FieldsProps) => {
  const { t } = useTranslation()

  let title: React.ReactNode = t("Lot")
  if (entity?.entity_type === EntityType.Administration && data.parent_tx) {
    title = (
      <span>
        {t("Lot")}
        <Link to={`${data.parent_tx}`} className={styles.parentLot}>
          (<Trans>Voir le lot parent</Trans>)
        </Link>
      </span>
    )
  }

  return (
    <FormGroup
      readOnly={readOnly || !editable}
      title={title}
      data={data}
      errors={errors}
      onChange={onChange}
    >
      <Fields.Dae readOnly={readOnly} />
      <Fields.Volume readOnly={readOnly} />
      <Fields.Biocarburant />
      <Fields.MatierePremiere />
      <Fields.PaysOrigine />
    </FormGroup>
  )
}

export default LotFields
