import { Navigate, Route, Routes } from "react-router-dom"
import Login from "./components/login"
import Register from "./components/register"

const Auth = () => {
  return (
    <Routes>
      <Route path="login" element={<Login />} />
      <Route path="register" element={<Register />} />
      <Route path="*" element={<Navigate to="login" />} />
    </Routes>
  )
}

export default Auth
