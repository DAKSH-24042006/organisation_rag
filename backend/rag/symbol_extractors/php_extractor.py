import re

from rag.symbol_extractors.base_extractor import (
    BaseExtractor
)


class PhpExtractor(
    BaseExtractor
):

    def extract(
        self,
        tree,
        source_code
    ):

        symbols = super().extract(
            tree,
            source_code
        )

        self._detect_laravel_controllers(
            symbols,
            source_code
        )

        self._detect_laravel_models(
            symbols,
            source_code
        )

        self._detect_laravel_middleware(
            symbols,
            source_code
        )

        self._detect_laravel_services(
            symbols,
            source_code
        )

        self._detect_routes(
            symbols,
            source_code
        )

        return symbols

    # =====================================================
    # CONTEXT
    # =====================================================

    def _get_context(
        self,
        source_code,
        start_line,
        window=15
    ):

        lines = source_code.splitlines()

        start = max(
            0,
            start_line - window
        )

        end = min(
            len(lines),
            start_line + window
        )

        return "\n".join(
            lines[start:end]
        )

    # =====================================================
    # CONTROLLERS
    # =====================================================

    def _detect_laravel_controllers(
        self,
        symbols,
        source_code
    ):

        for cls in symbols.get(
            "classes",
            []
        ):

            name = cls.get(
                "name",
                ""
            )

            if name.endswith(
                "Controller"
            ):

                cls[
                    "framework"
                ] = "Laravel"

                cls[
                    "component_type"
                ] = "CONTROLLER"

    # =====================================================
    # MODELS
    # =====================================================

    def _detect_laravel_models(
        self,
        symbols,
        source_code
    ):

        for cls in symbols.get(
            "classes",
            []
        ):

            content = cls.get(
                "content",
                ""
            )

            if (
                "extends Model"
                in content
            ):

                cls[
                    "framework"
                ] = "Laravel"

                cls[
                    "component_type"
                ] = "MODEL"

    # =====================================================
    # MIDDLEWARE
    # =====================================================

    def _detect_laravel_middleware(
        self,
        symbols,
        source_code
    ):

        for cls in symbols.get(
            "classes",
            []
        ):

            name = cls.get(
                "name",
                ""
            )

            content = cls.get(
                "content",
                ""
            )

            if (
                "handle("
                in content
                and
                (
                    name.endswith(
                        "Middleware"
                    )
                    or
                    "$next"
                    in content
                )
            ):

                cls[
                    "framework"
                ] = "Laravel"

                cls[
                    "component_type"
                ] = "MIDDLEWARE"

    # =====================================================
    # SERVICES
    # =====================================================

    def _detect_laravel_services(
        self,
        symbols,
        source_code
    ):

        for cls in symbols.get(
            "classes",
            []
        ):

            name = cls.get(
                "name",
                ""
            )

            if name.endswith(
                "Service"
            ):

                cls[
                    "framework"
                ] = "Laravel"

                cls[
                    "component_type"
                ] = "SERVICE"

    # =====================================================
    # ROUTES
    # =====================================================

    def _detect_routes(
        self,
        symbols,
        source_code
    ):

        route_patterns = [

            (
                r"Route::get\s*\(\s*['\"]([^'\"]+)['\"]",
                "GET"
            ),

            (
                r"Route::post\s*\(\s*['\"]([^'\"]+)['\"]",
                "POST"
            ),

            (
                r"Route::put\s*\(\s*['\"]([^'\"]+)['\"]",
                "PUT"
            ),

            (
                r"Route::delete\s*\(\s*['\"]([^'\"]+)['\"]",
                "DELETE"
            ),

            (
                r"Route::patch\s*\(\s*['\"]([^'\"]+)['\"]",
                "PATCH"
            )
        ]

        for function in symbols.get(
            "functions",
            []
        ):

            context = self._get_context(
                source_code,
                function["start_line"]
            )

            for pattern, method in route_patterns:

                match = re.search(
                    pattern,
                    context
                )

                if not match:
                    continue

                function[
                    "framework"
                ] = "Laravel"

                function[
                    "component_type"
                ] = "API_ENDPOINT"

                function[
                    "http_method"
                ] = method

                function[
                    "route"
                ] = match.group(
                    1
                )

                break