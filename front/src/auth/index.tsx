import { useTranslation } from "react-i18next"
import { Navigate, Route, Routes } from "react-router-dom"
import Login from "./components/login"
import OTP from "./components/otp"
import {
	ResetPasswordRequest,
	ResetPasswordPending,
	ResetPassword,
} from "./components/password"
import { Register, RegisterPending } from "./components/register"
import { Activate, ActivateRequest } from "./components/activate"
import { Logout } from "./components/logout"
import useTitle from "common/hooks/title"

const Auth = () => {
	const { t } = useTranslation()
	useTitle(t("Authentification"))

	return (
		<Routes>
			<Route path="login" element={<Login />} />
			<Route path="otp" element={<OTP />} />
			<Route path="logout" element={<Logout />} />
			<Route path="register" element={<Register />} />
			<Route path="register-pending" element={<RegisterPending />} />
			<Route path="activate-request" element={<ActivateRequest />} />
			<Route path="activate" element={<Activate />} />
			<Route path="reset-password-request" element={<ResetPasswordRequest />} />
			<Route path="reset-password-pending" element={<ResetPasswordPending />} />
			<Route path="reset-password" element={<ResetPassword />} />
			<Route path="*" element={<Navigate replace to="login" />} />
		</Routes>
	)
}
export default Auth
