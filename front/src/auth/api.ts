import { api as apiFetch } from "common/services/api-fetch"

export function register(
  email: string,
  name: string,
  password1: string,
  password2: string
) {
  return apiFetch.POST("/auth/register/", {
    body: {
      email,
      name,
      password1,
      password2,
    },
  })
}

export function login(username: string, password: string) {
  return apiFetch.POST("/auth/login/", {
    body: { username, password },
  })
}

export function logout() {
  return apiFetch.GET("/auth/logout/")
}

export function requestOTP() {
  return apiFetch.GET("/auth/request-otp/")
}

export function verifyOTP(otp_token: string) {
  return apiFetch.POST("/auth/verify-otp/", {
    body: { otp_token },
  })
}

export function requestResetPassword(username: string) {
  return apiFetch.POST("/auth/request-password-reset/", {
    body: { username },
  })
}

export function resetPassword(
  uidb64: string | undefined,
  token: string | undefined,
  password1: string,
  password2: string
) {
  if (uidb64 === undefined || token === undefined) {
    throw new Error("Missing token for password reset")
  }

  return apiFetch.POST("/auth/reset-password/", {
    body: {
      uidb64,
      token,
      password1,
      password2,
    },
  })
}

export function requestActivateAccount(email: string) {
  return apiFetch.POST("/auth/request-activation-link/", {
    body: { email },
  })
}

export function resendActivationLink(uidb64: string, token: string) {
  return apiFetch.POST("/auth/request-activation-link/", {
    body: { uidb64, token },
  })
}

export function checkActivateProfile(
  uidb64: string | undefined,
  token: string | undefined
) {
  if (uidb64 === undefined || token === undefined) {
    throw new Error("Missing token for account activation")
  }

  return apiFetch.POST("/auth/activate-profile/check/", {
    body: { uidb64, token },
  })
}

export function activateProfile(
  uidb64: string,
  token: string,
  name: string,
  password1: string,
  password2: string
) {
  return apiFetch.POST("/auth/activate-profile/", {
    body: {
      uidb64,
      token,
      name,
      password1,
      password2,
    },
  })
}

export function activateAccount(
  uidb64: string | undefined,
  token: string | undefined
) {
  if (uidb64 === undefined || token === undefined) {
    throw new Error("Missing token for account activation")
  }

  return apiFetch.POST("/auth/activate/", {
    body: {
      uidb64,
      token,
    },
  })
}
