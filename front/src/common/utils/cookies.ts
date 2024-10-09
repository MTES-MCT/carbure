/**
 * Return the value of a cookie
 * @param name name of cookie
 * @returns value
 */
export const getCookie = (name: string) => {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return parts.pop()!.split(";").shift()
  }
  return null
}
