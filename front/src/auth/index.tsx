import { Navigate, Route, Routes } from "react-router-dom"
import Login from "./components/login"
import OTP from "./components/otp"
import {
  ResetPasswordRequest,
  ResetPasswordPending,
  ResetPassword,
} from "./components/password"
import Register from "./components/register"

const Auth = () => {
  return (
    <Routes>
      <Route path="login" element={<Login />} />
      <Route path="register" element={<Register />} />
      <Route path="otp" element={<OTP />} />
      <Route path="reset-password-request" element={<ResetPasswordRequest />} />
      <Route path="reset-password-pending" element={<ResetPasswordPending />} />
      <Route path="reset-password" element={<ResetPassword />} />
      <Route path="*" element={<Navigate to="login" />} />
    </Routes>
  )
}

export default Auth
