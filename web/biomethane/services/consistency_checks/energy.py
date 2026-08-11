class BiomethaneEnergyConsistencyChecksService:
    @classmethod
    def get_consistency_warnings(cls, instance):
        warnings = []

        if w := cls._check_injected_biomethane_ch4_rate_percent(instance):
            warnings.append(w)
        return warnings

    @staticmethod
    def _check_injected_biomethane_ch4_rate_percent(instance):
        """Check if the injected biomethane CH4 rate percent is consistent with the expected value which is 95%"""

        injected_biomethane_ch4_rate_percent = getattr(instance, "injected_biomethane_ch4_rate_percent", None)

        if injected_biomethane_ch4_rate_percent < 95.0:
            return {
                "code": "INJECTED_BIOMETHANE_CH4_RATE_INCONSISTENT",
                "level": "warning",
                "message": "Le taux de CH4 dans le biométhane injecté est inférieur à 95%",
            }
        return None
