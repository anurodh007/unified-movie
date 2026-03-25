from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class CustomAutoSchema(AutoSchema):
    def get_override_parameters(self):
        params = list(super().get_override_parameters() or [])

        if not any(p.name == "tmdb_id" for p in params):
            params.append(
                OpenApiParameter(
                    name="tmdb_id",
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.PATH,
                    required=True,
                    description="TMDB movie ID",
                )
            )

        return params