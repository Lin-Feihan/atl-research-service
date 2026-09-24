from datetime import date


RUNTIME_DEFAULTS = {
    "shell-company-screening": {
        "control_requirement": "Not specified",
        "capital_structure_preference": "Not specified",
        "warrant_dilution_preference": "Not specified",
        "reporting_compliance_requirement": "Not specified",
        "historical_financing_preference": "Not specified",
        "market_cap_requirement": "No fixed threshold",
        "transaction_objective": "Not specified",
        "additional_requirements": "",
        "additional_context": "",
    },
    "due-diligence-agent": {
        "additional_context": "",
    },
}


def validate_value(field, value):
    field_type = field.get("type")

    if field_type in {"text", "longtext"}:
        return isinstance(value, str)

    if field_type == "number":
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
        )

    if field_type == "date":
        if not isinstance(value, str):
            return False

        try:
            date.fromisoformat(value)
            return True
        except ValueError:
            return False

    if field_type == "select":
        options = field.get("options", [])

        return (
            isinstance(value, str)
            and value in options
        )

    return False


def validate_and_build_settings(
    agent_id,
    manifest,
    submitted_settings,
):
    if not isinstance(submitted_settings, dict):
        return None, {
            "settings": "must be object"
        }

    fields = (
        manifest
        .get("settings_schema", {})
        .get("fields", [])
    )

    errors = {}

    for field in fields:
        field_id = field["id"]

        supplied = (
            field_id in submitted_settings
            and submitted_settings[field_id]
            not in (None, "")
        )

        if field.get("required") and not supplied:
            errors[field_id] = "required"
            continue

        if supplied and not validate_value(
            field,
            submitted_settings[field_id],
        ):
            errors[field_id] = "invalid"

    if errors:
        return None, errors

    settings = dict(
        RUNTIME_DEFAULTS.get(
            agent_id,
            {},
        )
    )

    for field in fields:
        field_id = field["id"]
        default = field.get("default")

        if default == "today":
            settings[field_id] = (
                date.today().isoformat()
            )

        elif (
            default is not None
            and field_id not in settings
        ):
            settings[field_id] = default

    for key, value in submitted_settings.items():
        if value not in (None, ""):
            settings[key] = value

    return settings, {}
