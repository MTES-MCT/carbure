import { useState } from "react"
import { useTranslation } from "react-i18next"
import Alert, { AlertProps } from "./alert"
import { Button } from "./button"

export interface SwitchProps extends AlertProps {
	dismissable?: boolean
	active: boolean
	children?: React.ReactNode
	onSwitch: (active: boolean) => void
}

export const Switch = ({
	dismissable,
	active,
	onSwitch,
	children,
	...props
}: SwitchProps) => {
	const { t } = useTranslation()
	const [open, setOpen] = useState(true)

	if (!open) return null

	return (
		<Alert {...props}>
			{children}

			<Button
				variant="link"
				label={active ? t("Revenir à la liste complète") : t("Voir la liste")}
				action={() => onSwitch(!active)}
			/>

			{dismissable && (
				<Button
					asideX
					variant="link"
					label={t("Masquer ce message")}
					action={() => {
						setOpen(false)
						onSwitch(false)
					}}
				/>
			)}
		</Alert>
	)
}

export default Switch
