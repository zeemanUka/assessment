from rest_framework.renderers import JSONRenderer


class EnvelopeJSONRenderer(JSONRenderer):
    """
    Wraps all API responses into:
    {
      "status": true|false,
      "message": "...",
      "data": ...
    }
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")

        # If no response context, fallback
        if response is None:
            return super().render(data, accepted_media_type, renderer_context)

        # If it's already wrapped, do nothing
        if isinstance(data, dict) and {"status", "message", "data"}.issubset(data.keys()):
            return super().render(data, accepted_media_type, renderer_context)

        status_code = getattr(response, "status_code", 200)
        ok = 200 <= status_code < 400

        if ok:
            payload = {
                "status": True,
                "message": "Success",
                "data": data,
            }
            return super().render(payload, accepted_media_type, renderer_context)

        # Error wrapping
        message = "Request failed"
        if isinstance(data, dict):
            if isinstance(data.get("detail"), str):
                message = data["detail"]
            elif data.get("non_field_errors"):
                try:
                    message = str(data["non_field_errors"][0])
                except Exception:
                    message = "Validation error"
            else:
                message = "Validation error"

        payload = {
            "status": False,
            "message": message,
            "data": data,
        }
        return super().render(payload, accepted_media_type, renderer_context)
