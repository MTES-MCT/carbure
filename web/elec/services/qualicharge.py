from rest_framework import serializers


def handle_bulk_create_validation_errors(request, serializer):
    errors = []
    for idx, (item_errors, item_data) in enumerate(zip(serializer.errors, request.data)):
        if not item_errors:
            continue

        entity = item_data.get("entity", "")
        siren = item_data.get("siren", "")

        # Errors at entity level
        for field, messages in item_errors.items():
            if field != "operational_units":
                errors.append({"index": idx, "entity": entity, "siren": siren, "field": field, "errors": messages})

        # Errors at operational unit level
        if "operational_units" in item_errors:
            operational_units = item_data.get("operational_units", [])
            for unit_error, unit_data in zip(item_errors["operational_units"], operational_units):
                if not unit_error:
                    continue

                code = unit_data.get("code", "")

                for field, messages in unit_error.items():
                    if field != "stations":
                        errors.append(
                            {"index": idx, "entity": entity, "unit_code": code, "field": field, "errors": messages}
                        )

                # Errors at station level
                if "stations" in unit_error:
                    stations = unit_data.get("stations", [])
                    for station_error, station_data in zip(unit_error["stations"], stations):
                        if not station_error:
                            continue

                        station_id = station_data.get("id", "")

                        for field, messages in station_error.items():
                            errors.append(
                                {
                                    "index": idx,
                                    "entity": entity,
                                    "unit_code": code,
                                    "station_id": station_id,
                                    "field": field,
                                    "errors": messages,
                                }
                            )

    raise serializers.ValidationError({"status": "validation_error", "errors": errors})
