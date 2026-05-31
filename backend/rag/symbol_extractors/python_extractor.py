import re

from rag.symbol_extractors.base_extractor import (
    BaseExtractor
)


class PythonExtractor(
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

        self._detect_fastapi_routes(
            symbols,
            source_code
        )

        self._detect_django_views(
            symbols,
            source_code
        )

        self._detect_pydantic_models(
            symbols,
            source_code
        )

        self._detect_async_functions(
            symbols,
            source_code
        )

        self._attach_decorators(
            symbols,
            source_code
        )

        return symbols

    # =====================================================
    # DECORATORS
    # =====================================================

    def _attach_decorators(
        self,
        symbols,
        source_code
    ):

        lines = source_code.splitlines()

        for function in symbols.get(
            "functions",
            []
        ):

            decorators = []

            start_line = (
                function["start_line"] - 1
            )

            for i in range(
                max(0, start_line - 5),
                start_line
            ):

                line = lines[i].strip()

                if line.startswith("@"):

                    decorators.append(
                        line
                    )

            function[
                "decorators"
            ] = decorators

    # =====================================================
    # FASTAPI ROUTES
    # =====================================================

    def _detect_fastapi_routes(
        self,
        symbols,
        source_code
    ):

        route_pattern = re.compile(
            r'@(router|app)\.(get|post|put|delete|patch)\(["\']([^"\']+)'
        )

        lines = source_code.splitlines()

        for function in symbols.get(
            "functions",
            []
        ):

            start_line = (
                function["start_line"] - 1
            )

            context_start = max(
                0,
                start_line - 5
            )

            context = "\n".join(
                lines[
                    context_start:
                    start_line + 1
                ]
            )

            match = route_pattern.search(
                context
            )

            if not match:
                continue

            function[
                "framework"
            ] = "FastAPI"

            function[
                "component_type"
            ] = "API_ROUTE"

            function[
                "http_method"
            ] = match.group(
                2
            ).upper()

            function[
                "route"
            ] = match.group(
                3
            )

    # =====================================================
    # DJANGO VIEWS
    # =====================================================

    def _detect_django_views(
        self,
        symbols,
        source_code
    ):

        for function in symbols.get(
            "functions",
            []
        ):

            content = function.get(
                "content",
                ""
            )

            decorators = function.get(
                "decorators",
                []
            )

            if any(
                "login_required" in d
                for d in decorators
            ):

                function[
                    "framework"
                ] = "Django"

                function[
                    "component_type"
                ] = "VIEW"

            if "render(" in content:

                function[
                    "framework"
                ] = "Django"

                function[
                    "component_type"
                ] = "VIEW"

            if "JsonResponse(" in content:

                function[
                    "framework"
                ] = "Django"

                function[
                    "component_type"
                ] = "API_VIEW"

    # =====================================================
    # PYDANTIC MODELS
    # =====================================================

    def _detect_pydantic_models(
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
                "BaseModel"
                in content
            ):

                cls[
                    "framework"
                ] = "Pydantic"

                cls[
                    "component_type"
                ] = "MODEL"

    # =====================================================
    # ASYNC FUNCTIONS
    # =====================================================

    def _detect_async_functions(
        self,
        symbols,
        source_code
    ):

        lines = source_code.splitlines()

        for function in symbols.get(
            "functions",
            []
        ):

            start_line = (
                function["start_line"] - 1
            )

            if (
                start_line < 0
                or
                start_line >= len(lines)
            ):
                continue

            line = lines[
                start_line
            ].strip()

            if line.startswith(
                "async def "
            ):

                function[
                    "is_async"
                ] = True

            else:

                function[
                    "is_async"
                ] = False