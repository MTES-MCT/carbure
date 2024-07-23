import { useTranslation } from "react-i18next"
import { EntityCertificate } from "carbure/types"
import { Grid, LoaderOverlay, Panel } from "common/components/scaffold"
import Table, { actionColumn, Cell } from "common/components/table"
import Button from "common/components/button"
import { Check, Cross } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { Confirm } from "common/components/dialog"
import { useMutation, useQuery } from "common/hooks/async"
import * as api from "../api"
import { useNotify } from "common/components/notifications"
import NoResult from "common/components/no-result"
import { compact, matchesSearch } from "common/utils/collection"
import Select from "common/components/select"
import { useState } from "react"
import useEntity from "carbure/hooks/entity"
import { useParams } from "react-router-dom"

type CertificatesProps = {
	search?: string
	entity_id?: number
}
type CertificatFilter = "all" | "to_checked" | "rejected" | "checked"

const Certificates = ({ search = "", entity_id }: CertificatesProps) => {
	const { t } = useTranslation()
	const entity = useEntity()

	const [certificatsFilter, setCertificatsFilter] = useState<
		CertificatFilter | undefined
	>("all")

	const certificates = useQuery(api.getEntityCertificates, {
		key: "entity-certificates",
		params: [entity.id, entity_id],
	})

	const certData = (certificates.result?.data?.data ?? []).filter(
		(c) =>
			matchesSearch(search, [
				c.certificate.certificate_id,
				c.certificate.certificate_holder,
				c.certificate.certificate_type,
				c.entity.name,
				c.entity.entity_type,
			]) && hasCertificatFilter(c, certificatsFilter)
	)

	return (
		<>
			<Grid>
				<Select
					value={certificatsFilter}
					onChange={setCertificatsFilter}
					label={t("Certificats")}
					placeholder={t("Filtrer les certificats")}
					options={compact([
						entity.isAdmin && {
							value: "all",
							label: t("Tous"),
						},
						entity.isAdmin && {
							value: "to_checked",
							label: t("À valider"),
						},
						entity.isAdmin && {
							value: "rejected",
							label: t("Refusés"),
						},
						entity.isAdmin && {
							value: "checked",
							label: t("Validés"),
						},
					])}
				/>
			</Grid>

			<Panel id="certificates">
				<header>
					<h1>{t("Certificats")}</h1>
				</header>
				{certData.length === 0 && (
					<>
						<section>
							<NoResult />
						</section>
						<footer />
					</>
				)}
				{certData.length > 0 && (
					<Table
						rows={certData}
						onAction={(e) => {
							if (e.certificate.download_link) {
								window.open(e.certificate.download_link)
							}
						}}
						columns={compact([
							entity_id === undefined && {
								key: "entities",
								header: t("Société"),
								orderBy: (e) => e.entity.name,
								cell: (e) => (
									<Cell text={e.entity.name} sub={t(e.entity.entity_type)} />
								),
							},
							{
								key: "id",
								header: t("ID"),
								orderBy: (c) => c.certificate.certificate_id,
								cell: (c) => <Cell text={c.certificate.certificate_id} />,
							},
							{
								key: "type",
								header: t("Type"),
								orderBy: (c) => c.certificate.certificate_type,
								cell: (c) => <Cell text={c.certificate.certificate_type} />,
							},
							{
								key: "holder",
								header: t("Détenteur"),
								orderBy: (c) => c.certificate.certificate_holder,
								cell: (c) => <Cell text={c.certificate.certificate_holder} />,
							},
							{
								key: "scope",
								header: t("Périmètre"),
								orderBy: (c) => c.certificate.scope ?? "-",
								cell: (c) => <Cell text={c.certificate.scope ?? "-"} />,
							},
							{
								key: "validity",
								header: t("Validité"),
								orderBy: (c) => c.certificate.valid_until,
								cell: (c) => <Cell text={c.certificate.valid_until} />,
							},
							actionColumn<EntityCertificate>((c) =>
								compact([
									!c.checked_by_admin && <CheckCertificate certificate={c} />,
									!c.rejected_by_admin && <RejectCertificate certificate={c} />,
								])
							),
						])}
					/>
				)}

				{certificates.loading && <LoaderOverlay />}
			</Panel>
		</>
	)
}

interface ActionProps {
	certificate: EntityCertificate
}

const CheckCertificate = ({ certificate }: ActionProps) => {
	const { t } = useTranslation()
	const portal = usePortal()
	const notify = useNotify()
	const entity = useEntity()

	const checkCertificate = useMutation(api.checkEntityCertificate, {
		invalidates: ["entity-certificates"],
		onSuccess(err) {
			notify(t("Le certificat a été validé !"), { variant: "success" })
		},
		onError() {
			notify(t("Le certificat n'a pas pu être validé !"), { variant: "danger" })
		},
	})

	return (
		<Button
			captive
			variant="icon"
			title={t("Valider le certificat")}
			icon={Check}
			action={() =>
				portal((close) => (
					<Confirm
						title={t("Valider le certificat")}
						description={t("Voulez-vous valider ce certificat ?")}
						variant="success"
						confirm={t("Valider")}
						onClose={close}
						onConfirm={() =>
							checkCertificate.execute(entity.id, certificate.id)
						}
					/>
				))
			}
		/>
	)
}

const RejectCertificate = ({ certificate }: ActionProps) => {
	const { t } = useTranslation()
	const portal = usePortal()
	const notify = useNotify()
	const entity = useEntity()

	const rejectCertificate = useMutation(api.rejectEntityCertificate, {
		invalidates: ["entity-certificates"],
		onSuccess(err) {
			notify(t("Le certificat a été refusé !"), { variant: "success" })
		},
		onError() {
			notify(t("Le certificat n'a pas pu être refusé !"), { variant: "danger" })
		},
	})

	return (
		<Button
			captive
			variant="icon"
			title={t("Refuser le certificat")}
			icon={Cross}
			action={() =>
				portal((close) => (
					<Confirm
						title={t("Refuser le certificat")}
						description={t("Voulez-vous refuser ce certificat ?")}
						variant="danger"
						confirm={t("Refuser")}
						icon={Cross}
						onClose={close}
						onConfirm={() =>
							rejectCertificate.execute(entity.id, certificate.id).then(close)
						}
					/>
				))
			}
		/>
	)
}

export default Certificates

function hasCertificatFilter(
	certificate: EntityCertificate,
	certificatFilter: CertificatFilter | undefined
) {
	if (certificate === undefined) return true
	if (certificatFilter === "all") return true // prettier-ignore
	if (certificatFilter === "to_checked" && certificate.checked_by_admin === false && certificate.rejected_by_admin == false) return true // prettier-ignore
	if (certificatFilter === "checked" && certificate.checked_by_admin === true) return true // prettier-ignore
	if (certificatFilter === "rejected" && certificate.rejected_by_admin === true) return true // prettier-ignore
}
