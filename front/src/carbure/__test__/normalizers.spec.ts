import { UserRole } from "carbure/types"
import { getUserRoleOptions } from "carbure/utils/normalizers"
import i18next from "i18next"
describe("Normalizers functions", () => {
  describe("getUserRoleOptions function", () => {
    it("Should return all roles if param is empty", () => {
      const result = getUserRoleOptions()

      expect(result).toEqual([
        {
          label: i18next.t("Lecture seule"),
          value: UserRole.ReadOnly,
        },
        {
          label: i18next.t("Lecture/écriture"),
          value: UserRole.ReadWrite,
        },
        {
          label: i18next.t(
            "Administration (contrôle complet de la société sur CarbuRe)"
          ),
          value: UserRole.Admin,
        },
        {
          label: i18next.t("Audit (accès spécial pour auditeurs)"),
          value: UserRole.Auditor,
        },
      ])
    })

    it("Should return only roles passed as parameter", () => {
      const result = getUserRoleOptions([UserRole.Admin])

      expect(result).toEqual([
        {
          label: i18next.t(
            "Administration (contrôle complet de la société sur CarbuRe)"
          ),
          value: UserRole.Admin,
        },
      ])
    })
  })
})
