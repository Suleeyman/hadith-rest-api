from src.core.schema import ErrorResponse, Resource


def not_found_response_annotation(resource: Resource):
    return {
        "model": ErrorResponse,
        "description": f"{resource} not found",
    }


def not_found_responses_annotation(*resources: Resource):
    return {
        "model": ErrorResponse,
        "description": " or ".join(f"{r} not found" for r in resources),
    }


def invalid_request_annotation(description: str):
    return {"model": ErrorResponse, "description": description}
