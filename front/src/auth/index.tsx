import { Navigate, Route, Routes } from "react-router-dom"
import Login from "./components/login"
import OTP from "./components/otp"
import Register from "./components/register"

const Auth = () => {
  return (
    <Routes>
      <Route path="login" element={<Login />} />
      <Route path="register" element={<Register />} />
      <Route path="otp" element={<OTP />} />
      <Route path="*" element={<Navigate to="login" />} />
    </Routes>
  )
}

export default Auth
