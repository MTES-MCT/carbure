import { findDepots } from "carbure/api"
import { Alert } from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { SearchInput } from "common/components/input"
import Table from "common/components/table"
import { useQuery } from "common/hooks/async"
import { Fragment, useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../../double-counting/api"
import { formatDateYear } from "common/utils/formatters"
import NoResult from "common/components/no-result"

const DoubleCounting = () => {
	const { t } = useTranslation()
	const agreementsResponse = useQuery(
		api.getDoubleCountingAgreementsPublicList,
		{
			key: "dc-agreements-public-list",
			params: [],
		}
	)
	const agreements = agreementsResponse.result?.data.data

	return (
		<>
			{agreements && (
				<Table
					loading={agreementsResponse.loading}
					columns={[
						{
							header: t("Unité de production"),
							small: true,
							cell: (a) => a.production_site.name || "-",
						},
						{
							header: t("Adresse"),
							small: true,
							cell: (a) => a.production_site.address,
						},
						{
							header: t("Pays"),
							small: true,
							cell: (a) => a.production_site.country || "-",
						},
						{
							header: t("N° d'agrément"),
							small: true,
							cell: (a) => a.certificate_id,
						},
						{
							header: t("Validité"),
							small: true,
							cell: (a) =>
								`${formatDateYear(a.valid_from)}-${formatDateYear(a.valid_until)}`,
						},
						{
							header: t("Biocarburants reconnus"),
							cell: (a) => a.biofuel_list,
						},
					]}
					rows={agreements}
				/>
			)}
			{!agreements && <NoResult loading={agreementsResponse.loading} />}
		</>
	)
}

export default DoubleCounting
