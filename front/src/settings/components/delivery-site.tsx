import { Trans, useTranslation } from "react-i18next"
import {
	Entity,
	EntityType,
	UserRole,
	Depot,
	DepotType,
	EntityDepot,
	OwnershipType,
} from "carbure/types"
import * as common from "carbure/api"
import * as api from "../api/delivery-sites"
import { Row, LoaderOverlay } from "common/components/scaffold"
import { TextInput } from "common/components/input"
import Checkbox from "common/components/checkbox"
import Button, { MailTo } from "common/components/button"
import { AlertCircle, Cross, Plus, Return } from "common/components/icons"
import { Alert } from "common/components/alert"
import Table, { actionColumn, Cell } from "common/components/table"
import { Confirm, Dialog } from "common/components/dialog"
import AutoComplete from "common/components/autocomplete"
import { RadioGroup } from "common/components/radio"
import { Form, useForm } from "common/components/form"
import useEntity, { useRights } from "carbure/hooks/entity"
import { Panel } from "common/components/scaffold"
import { normalizeDepot, normalizeEntity } from "carbure/utils/normalizers"
import { compact } from "common/utils/collection"
import { useMutation, useQuery } from "common/hooks/async"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { formatNumber, formatPercentage } from "common/utils/formatters"

interface DeliverySiteSettingsProps {
	readOnly?: boolean
	entity: Entity
	getDepots?: typeof api.getDeliverySites
}

const DeliverySitesSettings = ({
	readOnly,
	entity,
	getDepots = api.getDeliverySites,
}: DeliverySiteSettingsProps) => {
	const { t } = useTranslation()
	const rights = useRights()
	const portal = usePortal()

	const deliverySites = useQuery(getDepots, {
		key: "delivery-sites",
		params: [entity.id],
	})

	const deliverySitesData = deliverySites.result?.data.data ?? []
	const isEmpty = deliverySitesData.length === 0

	const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

	const depotTypeLabels = {
		[DepotType.EFS]: t("EFS"),
		[DepotType.EFPE]: t("EFPE"),
		[DepotType.Other]: t("Autre"),
		[DepotType.BiofuelDepot]: t("Biofuel Depot"),
		[DepotType.OilDepot]: t("Oil Depot"),
		[DepotType.PowerPlant]: t("Centrale électrique"),
		[DepotType.HeatPlant]: t("Centrale de chaleur"),
		[DepotType.CogenerationPlant]: t("Centrale de cogénération"),
	}

	function findDeliverySite() {
		portal((close) => <DeliverySiteFinderDialog onClose={close} />)
	}

	function showDeliverySite(deliverySite: EntityDepot) {
		portal((close) => (
			<DeliverySiteDialog deliverySite={deliverySite} onClose={close} />
		))
	}

	return (
		<Panel id="depot">
			<header>
				<h1>
					<Trans>Dépôts</Trans>
				</h1>
				{!readOnly && canModify && (
					<Button
						asideX
						variant="primary"
						icon={Plus}
						label={t("Ajouter un dépôt")}
						action={findDeliverySite}
					/>
				)}
			</header>

			{isEmpty && (
				<>
					<section>
						<Alert icon={AlertCircle} variant="warning">
							<Trans>Aucun dépôt trouvé</Trans>
						</Alert>
					</section>
					<footer />
				</>
			)}

			{!isEmpty && (
				<Table
					rows={deliverySitesData}
					onAction={showDeliverySite}
					columns={[
						{
							key: "id",
							header: t("ID"),
							orderBy: (ds) => ds.depot?.depot_id ?? "",
							cell: (ds) => <Cell text={ds.depot!.depot_id} />,
						},
						{
							key: "name",
							header: t("Nom"),
							orderBy: (ds) => ds.depot?.name ?? "",
							cell: (ds) => <Cell text={ds.depot!.name} />,
						},
						{
							key: "type",
							header: t("Type"),
							cell: (ds) => (
								<Cell text={depotTypeLabels[ds.depot!.depot_type]} />
							),
						},
						{
							key: "city",
							header: t("Ville"),
							orderBy: (ds) => ds.depot?.city ?? "",
							cell: (ds) => (
								<Cell
									text={`${ds.depot!.city}, ${t(ds.depot!.country.code_pays, {
										ns: "countries",
									})}`}
								/>
							),
						},
						actionColumn<EntityDepot>((ds) =>
							compact([
								!readOnly && canModify && (
									<DeleteDeliverySiteButton deliverySite={ds} />
								),
							])
						),
					]}
				/>
			)}

			{deliverySites.loading && <LoaderOverlay />}
		</Panel>
	)
}

type DeliverySiteDialogProps = {
	deliverySite: EntityDepot
	onClose: () => void
}

export const DeliverySiteDialog = ({
	deliverySite,
	onClose,
}: DeliverySiteDialogProps) => {
	const { t } = useTranslation()

	const form = {
		name: deliverySite?.depot?.name ?? "",
		city: deliverySite?.depot?.city ?? "",
		country: deliverySite?.depot?.country ?? null,
		depot_id: deliverySite?.depot?.depot_id ?? "",
		depot_type: deliverySite?.depot?.depot_type ?? DepotType.Other,
		address: deliverySite?.depot?.address ?? "",
		postal_code: deliverySite?.depot?.postal_code ?? "",
		ownership_type: deliverySite?.ownership_type ?? OwnershipType.Own,
		blending_is_outsourced: deliverySite?.blending_is_outsourced ?? false,
		blender: deliverySite?.blender?.name ?? "",
	}

	const depotTypes = [
		{ value: DepotType.EFS, label: t("EFS") },
		{ value: DepotType.EFPE, label: t("EFPE") },
		{ value: DepotType.Other, label: t("Autre") },
		{ value: DepotType.BiofuelDepot, label: t("Biofuel Depot") },
		{ value: DepotType.OilDepot, label: t("Oil Depot") },
		{ value: DepotType.PowerPlant, label: t("Centrale électrique") },
		{ value: DepotType.HeatPlant, label: t("Centrale de chaleur") },
		{ value: DepotType.CogenerationPlant, label: t("Centrale de cogénération") }, // prettier-ignore
	]

	const ownerShipTypes = [
		{ value: OwnershipType.Own, label: t("Propre") },
		{ value: OwnershipType.ThirdParty, label: t("Tiers") },
		{ value: OwnershipType.Processing, label: t("Processing") },
	]

	const depotType = deliverySite.depot?.depot_type ?? DepotType.Other
	const isPowerOrHeatPlant = [DepotType.PowerPlant, DepotType.HeatPlant, DepotType.CogenerationPlant].includes(depotType) // prettier-ignore

	const electricalEfficiency = deliverySite.depot?.electrical_efficiency
	const thermalEfficiency = deliverySite.depot?.thermal_efficiency
	const usefulTemperature = deliverySite.depot?.useful_temperature

	return (
		<Dialog onClose={onClose}>
			<header>
				<h1>{t("Détails du dépôt")}</h1>
			</header>

			<main>
				<section>
					<Form>
						<RadioGroup
							disabled
							label={t("Propriété")}
							value={form.ownership_type}
							name="ownership_type"
							options={ownerShipTypes}
						/>

						<hr />

						<Checkbox
							disabled
							label={t("L'incorporation est effectuée par un tiers")}
							name="blending_is_outsourced"
							value={form.blending_is_outsourced}
						/>
						{form.blending_is_outsourced && (
							<TextInput
								readOnly
								label={t("Incorporateur")}
								name="blender"
								value={form.blender}
							/>
						)}

						<hr />

						<TextInput
							readOnly
							label={t("Nom du site")}
							name="name"
							value={form.name}
						/>
						<TextInput
							readOnly
							label={t("ID de douane")}
							name="depot_id"
							value={form.depot_id}
						/>

						<hr />

						<RadioGroup
							disabled
							label={t("Type de dépôt")}
							value={form.depot_type}
							name="depot_type"
							options={depotTypes}
						/>

						<hr />

						<TextInput
							readOnly
							label={t("Adresse")}
							name="address"
							value={form.address}
						/>

						<Row style={{ gap: "var(--spacing-s)" }}>
							<TextInput
								readOnly
								label={t("Ville")}
								name="city"
								value={form.city}
							/>
							<TextInput
								readOnly
								label={t("Code postal")}
								name="postal_code"
								value={form.postal_code}
							/>
						</Row>

						<TextInput
							readOnly
							label={t("Pays")}
							placeholder={t("Rechercher un pays...")}
							name="country"
							value={
								form.country
									? (t(form.country.code_pays, { ns: "countries" }) as string)
									: ""
							}
						/>
					</Form>
				</section>

				{isPowerOrHeatPlant && (
					<>
						<hr />
						<section>
							{electricalEfficiency && (
								<TextInput
									readOnly
									label={t("Rendement électrique")}
									value={formatPercentage(electricalEfficiency * 100)}
								/>
							)}
							{thermalEfficiency && (
								<TextInput
									readOnly
									label={t("Rendement thermique")}
									value={formatPercentage(thermalEfficiency * 100)}
								/>
							)}
							{usefulTemperature && (
								<TextInput
									readOnly
									label={t("Température utile")}
									value={formatNumber(usefulTemperature) + "˚C"}
								/>
							)}
						</section>
					</>
				)}

				<section></section>
			</main>

			<footer>
				<Button asideX icon={Return} action={onClose}>
					<Trans>Retour</Trans>
				</Button>
			</footer>
		</Dialog>
	)
}

type DeliverySiteFinderDialogProps = {
	onClose: () => void
}

export const DeliverySiteFinderDialog = ({
	onClose,
}: DeliverySiteFinderDialogProps) => {
	const { t } = useTranslation()
	const entity = useEntity()
	const notify = useNotify()

	const addDeliverySite = useMutation(api.addDeliverySite, {
		invalidates: ["delivery-sites"],

		onSuccess: () => {
			notify(t("Le dépôt a bien été ajouté !"), { variant: "success" })
			onClose()
		},

		onError: () => {
			notify(t("Impossible d'ajouter le dépôt."), { variant: "danger" })
		},
	})

	const { value, bind } = useForm({
		depot: undefined as Depot | undefined,
		ownership_type: OwnershipType.ThirdParty as OwnershipType | undefined,
		blending_is_outsourced: false,
		blender: undefined as Entity | undefined,
	})

	const ownerShipTypes = [
		{ value: OwnershipType.Own, label: "Propre" },
		{ value: OwnershipType.ThirdParty, label: "Tiers" },
		{ value: OwnershipType.Processing, label: "Processing" },
	]

	async function submitDepot() {
		if (!value.depot) return

		await addDeliverySite.execute(
			entity.id,
			value.depot.depot_id,
			value.ownership_type!,
			value.blending_is_outsourced,
			value.blender
		)
	}

	return (
		<Dialog onClose={onClose}>
			<header>
				<h1>{t("Ajouter dépôt")}</h1>
			</header>

			<main>
				<section>
					<p>{t("Veuillez rechercher un dépôt que vous utilisez.")}</p>
				</section>

				<section>
					<Form id="add-depot" onSubmit={submitDepot}>
						<AutoComplete
							autoFocus
							label={t("Dépôt à ajouter")}
							placeholder={t("Rechercher un dépôt...")}
							getOptions={(search) => common.findDepots(search)}
							normalize={normalizeDepot}
							{...bind("depot")}
						/>

						<RadioGroup
							label={t("Propriété")}
							options={ownerShipTypes}
							{...bind("ownership_type")}
						/>

						{entity && entity.entity_type === EntityType.Operator && (
							<Checkbox
								label={t("Incorporation potentiellement effectuée par un tiers")} // prettier-ignore
								{...bind("blending_is_outsourced")}
							/>
						)}
						{value.blending_is_outsourced && (
							<AutoComplete
								label={t("Incorporateur Tiers")}
								placeholder={t("Rechercher un opérateur pétrolier...")}
								getOptions={common.findOperators}
								normalize={normalizeEntity}
								{...bind("blender")}
							/>
						)}

						<MailTo user="carbure" host="beta.gouv.fr">
							<Trans>
								Le dépôt que je recherche n'est pas enregistré sur CarbuRe.
							</Trans>
						</MailTo>
					</Form>
				</section>
			</main>

			<footer>
				<Button
					asideX
					loading={addDeliverySite.loading}
					variant="primary"
					submit="add-depot"
					icon={Plus}
					label={t("Ajouter")}
				/>
				<Button action={onClose} label={t("Annuler")} />
			</footer>
		</Dialog>
	)
}

const DeleteDeliverySiteButton = ({
	deliverySite,
}: {
	deliverySite: EntityDepot
}) => {
	const { t } = useTranslation()
	const notify = useNotify()
	const portal = usePortal()

	const entity = useEntity()

	const deleteDeliverySite = useMutation(api.deleteDeliverySite, {
		invalidates: ["delivery-sites"],

		onSuccess: () => {
			notify(t("Le dépôt a bien été supprimé !"), { variant: "success" })
		},

		onError: () => {
			notify(t("Impossible de supprimer le dépôt."), { variant: "danger" })
		},
	})

	return (
		<Button
			captive
			variant="icon"
			icon={Cross}
			title={t("Supprimer le dépôt")}
			action={() =>
				portal((close) => (
					<Confirm
						title={t("Supprimer dépôt")}
						description={t("Voulez-vous supprimer le dépôt {{depot}} de votre liste ?", { depot: deliverySite.depot!.name })} // prettier-ignore
						confirm={t("Supprimer")}
						icon={Cross}
						variant="danger"
						onClose={close}
						onConfirm={async () => {
							if (deliverySite.depot) {
								await deleteDeliverySite.execute(
									entity.id,
									deliverySite.depot.depot_id
								)
							}
						}}
					/>
				))
			}
		/>
	)
}

export default DeliverySitesSettings
