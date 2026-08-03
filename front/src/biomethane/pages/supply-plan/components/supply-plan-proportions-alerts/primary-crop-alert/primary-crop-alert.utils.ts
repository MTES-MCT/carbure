/** Maximum allowed primary-crop share of declared wet matter tonnage (tMB). */
export const PRIMARY_CROP_MAX_PERCENT = 15

export const getPrimaryCropAlertSeverity = (
  percent: number
): "error" | "success" =>
  percent > PRIMARY_CROP_MAX_PERCENT ? "error" : "success"
