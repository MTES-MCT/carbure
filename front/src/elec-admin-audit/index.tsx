import useEntity from "carbure/hooks/entity"
import { Main } from "common/components/scaffold"
import Select from "common/components/select"
import useYears from "common/hooks/years"
import { useTranslation } from "react-i18next"
import * as api from "./api"




export const ElecAdminAudit = () => {
  const { t } = useTranslation()

  const entity = useEntity()

  const years = useYears("elec-admin-audit", api.getYears)

  return (

    <Main>
      <header>
        <section>
          <h1>{t("Inscriptions et relevés des points de recharge")}</h1>

          <Select
            loading={years.loading}
            variant="inline"
            placeholder={t("Choisir une année")}
            value={years.selected}
            onChange={years.setYear}
            options={years.options}
            sort={(year) => -year.value}
          />
        </section>

      </header>

    </Main>


  )
}

export default ElecAdminAudit



