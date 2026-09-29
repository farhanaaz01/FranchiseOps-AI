"""Map integer DB outlet IDs to pipeline string IDs (OUT-01)."""


def format_pipeline_outlet_id(outlet_id: int) -> str:
    return f"OUT-{int(outlet_id):02d}"


def parse_pipeline_outlet_id(outlet_id: str) -> int | None:
    if not outlet_id:
        return None
    value = outlet_id.strip().upper()
    if value.startswith("OUT-"):
        try:
            return int(value.split("-", 1)[1])
        except ValueError:
            return None
    try:
        return int(value)
    except ValueError:
        return None
