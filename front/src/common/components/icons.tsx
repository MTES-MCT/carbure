import React from "react"
import cl from "clsx"
import css from "./icons.module.css"

// icons were adapted from https://github.com/tabler/tabler-icons

export interface IconProps
	extends Omit<React.SVGProps<SVGSVGElement>, "stroke"> {
	passthrough?: boolean
	size?: number
	color?: string
	fill?: string
	stroke?: number
	title?: string
}

const Icon = ({
	className,
	passthrough,
	size = 24,
	color = "currentColor",
	stroke = 2,
	fill = "none",
	title,
	children,
	...props
}: IconProps) => (
	<svg
		data-icon
		className={cl("icon", passthrough && css.passthrough, className)}
		width={size}
		height={size}
		viewBox="0 0 24 24"
		strokeWidth={stroke}
		stroke={color}
		fill={fill}
		strokeLinecap="round"
		strokeLinejoin="round"
		{...props}
	>
		{title && <title>{title}</title>}
		{children}
	</svg>
)

export const Placeholder = ({ className, ...props }: IconProps) => (
	<Icon passthrough {...props} className={cl("placeholder", className)} />
)

export const ChevronDown = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("chevron-down", className)}>
		<polyline points="6 9 12 15 18 9" />
	</Icon>
)

export const ChevronLeft = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("chevron-left", className)}>
		<polyline points="15 6 9 12 15 18" />
	</Icon>
)

export const ChevronRight = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("chevron-right", className)}>
		<polyline points="9 6 15 12 9 18" />
	</Icon>
)

export const Plus = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("plus", className)}>
		<line x1={12} y1={5} x2={12} y2={19} />
		<line x1={5} y1={12} x2={19} y2={12} />
	</Icon>
)

export const Search = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("search", className)}>
		<circle cx="10" cy="10" r="7" />
		<line x1="21" y1="21" x2="15" y2="15" />
	</Icon>
)

export const Cross = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("cross", className)}>
		<line x1="18" y1="6" x2="6" y2="18" />
		<line x1="6" y1="6" x2="18" y2="18" />
	</Icon>
)

export const AlertCircle = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("alert-circle", className)}>
		<circle cx="12" cy="12" r="9" />
		<line x1="12" y1="8" x2="12" y2="12" />
		<line x1="12" y1="16" x2="12.01" y2="16" />
	</Icon>
)

export const Copy = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("copy", className)}>
		<rect x="8" y="8" width="12" height="12" rx="2" />
		<path d="M16 8v-2a2 2 0 0 0 -2 -2h-8a2 2 0 0 0 -2 2v8a2 2 0 0 0 2 2h2" />
	</Icon>
)

export const Check = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("check", className)}>
		<path d="M5 12l5 5l10 -10" />
	</Icon>
)

export const Save = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("save", className)}>
		<path d="M6 4h10l4 4v10a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2v-12a2 2 0 0 1 2 -2" />
		<circle cx="12" cy="14" r="2" />
		<polyline points="14 4 14 8 8 8 8 4" />
	</Icon>
)

export const Message = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("message", className)}>
		<path d="M4 21v-13a3 3 0 0 1 3 -3h10a3 3 0 0 1 3 3v6a3 3 0 0 1 -3 3h-9l-4 4" />
		<line x1="12" y1="8" x2="12" y2="11" />
		<line x1="12" y1="14" x2="12" y2="14.01" />
	</Icon>
)

export const Loader = ({ className, ...props }: IconProps) => (
	<Icon
		{...props}
		className={cl("loader", css.loader, className)}
		title="Chargement..."
		data-testid="loader"
	>
		<line x1="12" y1="6" x2="12" y2="3" />
		<line x1="16.25" y1="7.75" x2="18.4" y2="5.6" />
		<line x1="18" y1="12" x2="21" y2="12" />
		<line x1="16.25" y1="16.25" x2="18.4" y2="18.4" />
		<line x1="12" y1="18" x2="12" y2="21" />
		<line x1="7.75" y1="16.25" x2="5.6" y2="18.4" />
		<line x1="6" y1="12" x2="3" y2="12" />
		<line x1="7.75" y1="7.75" x2="5.6" y2="5.6" />
	</Icon>
)

export const Upload = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("upload", className)}>
		<path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2" />
		<polyline points="7 11 12 16 17 11" />
		<line x1="12" y1="4" x2="12" y2="16" />
	</Icon>
)

export const Download = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("download", className)}>
		<path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2" />
		<polyline points="7 9 12 4 17 9" />
		<line x1="12" y1="4" x2="12" y2="16" />
	</Icon>
)

export const AlertTriangle = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("alert-triangle", className)}>
		<path d="M12 9v2m0 4v.01" />
		<path d="M5 19h14a2 2 0 0 0 1.84 -2.75l-7.1 -12.25a2 2 0 0 0 -3.5 0l-7.1 12.25a2 2 0 0 0 1.75 2.75" />
	</Icon>
)

export const AlertTriangleOff = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("alert-triangle-off", className)}>
		<path d="M12 9v2m0 4v.01" />
		<path d="M5 19h14a2 2 0 0 0 1.84 -2.75l-7.1 -12.25a2 2 0 0 0 -3.5 0l-7.1 12.25a2 2 0 0 0 1.75 2.75" />
		<line x1="3" y1="3" x2="21" y2="21" />
	</Icon>
)

export const AlertOctagon = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("alert-octagon", className)}>
		<path d="M8.7 3h6.6c0.3 0 .5 .1 .7 .3l4.7 4.7c0.2 .2 .3 .4 .3 .7v6.6c0 .3 -.1 .5 -.3 .7l-4.7 4.7c-0.2 .2 -.4 .3 -.7 .3h-6.6c-0.3 0 -.5 -.1 -.7 -.3l-4.7 -4.7c-0.2 -.2 -.3 -.4 -.3 -.7v-6.6c0 -.3 .1 -.5 .3 -.7l4.7 -4.7c0.2 -.2 .4 -.3 .7 -.3z" />
		<line x1="12" y1="8" x2="12" y2="12" />
		<line x1="12" y1="16" x2="12.01" y2="16" />
	</Icon>
)

export const Return = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("return", className)}>
		<path d="M9 11l-4 4l4 4m-4 -4h11a4 4 0 0 0 0 -8h-1" />
	</Icon>
)

export const Edit = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("edit", className)}>
		<path d="M4 20h4l10.5 -10.5a1.5 1.5 0 0 0 -4 -4l-10.5 10.5v4" />
		<line x1="13.5" y1="6.5" x2="17.5" y2="10.5" />
	</Icon>
)

export const Refresh = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("refresh", className)}>
		<path d="M20 11a8.1 8.1 0 0 0 -15.5 -2m-.5 -4v4h4" />
		<path d="M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4" />
	</Icon>
)

export const Question = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("question", className)}>
		<path d="M8 8a3.5 3 0 0 1 3.5 -3h1a3.5 3 0 0 1 3.5 3a3 3 0 0 1 -2 3a3 4 0 0 0 -2 4" />
		<line x1="12" y1="19" x2="12" y2="19.01" />
	</Icon>
)

export const Filter = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("filter", className)}>
		<path d="M5.5 5h13a1 1 0 0 1 .5 1.5l-5 5.5l0 7l-4 -3l0 -4l-5 -5.5a1 1 0 0 1 .5 -1.5" />
	</Icon>
)

export const Bolt = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("filter", className)}>
		<path d="M13 3l0 7l6 0l-8 11l0 -7l-6 0l8 -11" />
	</Icon>
)

export const Alarm = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("alarm", className)}>
		<circle cx="12" cy="13" r="7" />
		<polyline points="12 10 12 13 14 13" />
		<line x1="7" y1="4" x2="4.25" y2="6" />
		<line x1="17" y1="4" x2="19.75" y2="6" />
	</Icon>
)

export const CheckCircle = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("check-circle", className)}>
		<polyline points="9 11 12 14 20 6" />
		<path d="M20 12v6a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2v-12a2 2 0 0 1 2 -2h9" />
	</Icon>
)

export const Bell = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("bell", className)}>
		<path d="M10 5a2 2 0 0 1 4 0a7 7 0 0 1 4 6v3a4 4 0 0 0 2 3h-16a4 4 0 0 0 2 -3v-3a7 7 0 0 1 4 -6" />
		<path d="M9 17v1a3 3 0 0 0 6 0v-1" />
		<path d="M21 6.727a11.05 11.05 0 0 0 -2.794 -3.727" />
		<path d="M3 6.727a11.05 11.05 0 0 1 2.792 -3.727" />
	</Icon>
)

export const Flask = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("flask", className)}>
		<line x1="9" y1="3" x2="15" y2="3" />
		<line x1="10" y1="9" x2="14" y2="9" />
		<path d="M10 3v6l-4 11a0.7 .7 0 0 0 .5 1h11a0.7 .7 0 0 0 .5 -1l-4 -11v-6" />
	</Icon>
)

export const Certificate = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("certificate", className)}>
		<circle cx="15" cy="15" r="3" />
		<path d="M13 17.5v4.5l2 -1.5l2 1.5v-4.5" />
		<path d="M10 19h-5a2 2 0 0 1 -2 -2v-10c0 -1.1 .9 -2 2 -2h14a2 2 0 0 1 2 2v10a2 2 0 0 1 -1 1.73" />
		<line x1="6" y1="9" x2="18" y2="9" />
		<line x1="6" y1="12" x2="9" y2="12" />
		<line x1="6" y1="15" x2="8" y2="15" />
	</Icon>
)

export const UserCheck = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("user-check", className)}>
		<circle cx="9" cy="7" r="4" />
		<path d="M3 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2" />
		<path d="M16 11l2 2l4 -4" />
	</Icon>
)

export const FileCheck = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("pin", className)}>
		<path d="M14 3v4a1 1 0 0 0 1 1h4" />
		<path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z" />
		<path d="M9 15l2 2l4 -4" />
	</Icon>
)

export const Slack = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("slack", className)}>
		<path d="M12 12v-6a2 2 0 0 1 4 0v6m0 -2a2 2 0 1 1 2 2h-6" />
		<path d="M12 12h6a2 2 0 0 1 0 4h-6m2 0a2 2 0 1 1 -2 2v-6" />
		<path d="M12 12v6a2 2 0 0 1 -4 0v-6m0 2a2 2 0 1 1 -2 -2h6" />
		<path d="M12 12h-6a2 2 0 0 1 0 -4h6m-2 0a2 2 0 1 1 2 -2v6" />
	</Icon>
)

export const LinkedIn = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("slack", className)}>
		<rect x="4" y="4" width="16" height="16" rx="2" />
		<line x1="8" y1="11" x2="8" y2="16" />
		<line x1="8" y1="8" x2="8" y2="8.01" />
		<line x1="12" y1="16" x2="12" y2="11" />
		<path d="M16 16v-3a2 2 0 0 0 -4 0" />
	</Icon>
)

export const ExternalLink = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("external-link", className)}>
		<path d="M11 7h-5a2 2 0 0 0 -2 2v9a2 2 0 0 0 2 2h9a2 2 0 0 0 2 -2v-5" />
		<line x1="10" y1="14" x2="20" y2="4" />
		<polyline points="15 4 20 4 20 9" />
	</Icon>
)

export const UserAdd = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("user-add", className)}>
		<circle cx="9" cy="7" r="4" />
		<path d="M3 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2" />
		<path d="M16 11h6m-3 -3v6" />
	</Icon>
)

export const Disk = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("disk", className)}>
		<circle cx={12} cy={12} r={9} strokeWidth={0} />
	</Icon>
)

export const History = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("history", className)}>
		<polyline points="12 8 12 12 14 14" />
		<path d="M3.05 11a9 9 0 1 1 .5 4m-.5 5v-5h5" />
	</Icon>
)

export const Wrench = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("wrench", className)}>
		<path d="M7 10h3v-3l-3.5 -3.5a6 6 0 0 1 8 8l6 6a2 2 0 0 1 -3 3l-6 -6a6 6 0 0 1 -8 -8l3.5 3.5" />
	</Icon>
)

export const Split = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("split", className)}>
		<path d="M21 17h-8l-3.5 -5h-6.5" />
		<path d="M21 7h-8l-3.495 5" />
		<path d="M18 10l3 -3l-3 -3" />
		<path d="M18 20l3 -3l-3 -3" />
	</Icon>
)

export const Send = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("send", className)}>
		<path stroke="none" d="M0 0h24v24H0z" fill="none" />
		<line x1="10" y1="14" x2="21" y2="3" />
		<path d="M21 3l-6.5 18a0.55 .55 0 0 1 -1 0l-3.5 -7l-7 -3.5a0.55 .55 0 0 1 0 -1l18 -6.5" />
	</Icon>
)

export const Drop = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("drop", className)}>
		<path d="M6.8 11a6 6 0 1 0 10.396 0l-5.197 -8l-5.2 8z" />
		<path d="M6 14h12" />
		<path d="M7.305 17.695l3.695 -3.695" />
		<path d="M10.26 19.74l5.74 -5.74l-5.74 5.74z" />
	</Icon>
)

export const InfoCircle = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("info-circle", className)}>
		<circle cx="12" cy="12" r="9" />
		<line x1="12" y1="8" x2="12.01" y2="8" />
		<polyline points="11 12 12 12 12 16 13 16" />
	</Icon>
)

export const Mail = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("mail", className)}>
		<rect x="3" y="5" width="18" height="14" rx="2" />
		<polyline points="3 7 12 13 21 7" />
	</Icon>
)

export const Lock = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("lock", className)}>
		<rect x="5" y="11" width="14" height="10" rx="2" />
		<circle cx="12" cy="16" r="1" />
		<path d="M8 11v-4a4 4 0 0 1 8 0v4" />
	</Icon>
)

export const User = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("user", className)}>
		<circle cx="12" cy="7" r="4" />
		<path d="M6 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2" />
	</Icon>
)

export const Square = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("square", className)}>
		<rect width={24} height={24} fill={props.color} strokeWidth={0} />
	</Icon>
)

export const Map = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("map", className)}>
		<polyline points="3 7 9 4 15 7 21 4 21 17 15 20 9 17 3 20 3 7" />
		<line x1="9" y1="4" x2="9" y2="17" />
		<line x1="15" y1="7" x2="15" y2="20" />
	</Icon>
)

export const DropOff = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("drop-off", className)}>
		<path d="M8.454 8.458l-1.653 2.545a6 6 0 0 0 10.32 6.123" />
		<path d="M18 14a5.971 5.971 0 0 0 -.803 -3l-5.197 -8l-1.968 3.03" />
		<path d="M3 3l18 18" />
	</Icon>
)

export const Calculator = ({ className, ...props }: IconProps) => (
	<Icon {...props} className={cl("drop-off", className)}>
		<rect x="4" y="3" width="16" height="18" rx="2" />
		<rect x="8" y="7" width="8" height="3" rx="1" />
		<line x1="8" y1="14" x2="8" y2="14.01" />
		<line x1="12" y1="14" x2="12" y2="14.01" />
		<line x1="16" y1="14" x2="16" y2="14.01" />
		<line x1="8" y1="17" x2="8" y2="17.01" />
		<line x1="12" y1="17" x2="12" y2="17.01" />
		<line x1="16" y1="17" x2="16" y2="17.01" />
	</Icon>
)
