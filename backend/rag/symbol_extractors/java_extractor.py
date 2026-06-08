import re

from rag.symbol_extractors.base_extractor import (
    BaseExtractor
)


class JavaExtractor(
    BaseExtractor
):

    def extract(
        self,
        tree,
        source_code,
        file_path=None
    ):

        symbols = super().extract(
            tree,
            source_code,
            file_path=file_path
        )

        self._detect_spring_controllers(
            symbols,
            source_code
        )

        self._detect_spring_services(
            symbols,
            source_code
        )

        self._detect_spring_repositories(
            symbols,
            source_code
        )

        self._detect_spring_components(
            symbols,
            source_code
        )

        self._detect_request_mappings(
            symbols,
            source_code
        )

        self._detect_jpa_entities(
            symbols,
            source_code
        )

        return symbols

    # =====================================================
    # GET CONTEXT
    # =====================================================

    def _get_context(
        self,
        source_code,
        start_line,
        window=10
    ):

        lines = source_code.splitlines()

        start = max(
            0,
            start_line - window
        )

        end = min(
            len(lines),
            start_line + 1
        )

        return "\n".join(
            lines[start:end]
        )

    # =====================================================
    # SPRING CONTROLLERS
    # =====================================================

    def _detect_spring_controllers(
        self,
        symbols,
        source_code
    ):

        for cls in symbols.get(
            "classes",
            []
        ):

            context = self._get_context(
                source_code,
                cls["start_line"]
            )

            if (
                "@RestController"
                in context
            ):

                cls[
                    "framework"
                ] = "SpringBoot"

                cls[
                    "component_type"
                ] = "REST_CONTROLLER"

            elif (
                "@Controller"
                in context
            ):

                cls[
                    "framework"
                ] = "SpringBoot"

                cls[
                    "component_type"
                ] = "CONTROLLER"

    # =====================================================
    # SERVICES
    # =====================================================

    def _detect_spring_services(
        self,
        symbols,
        source_code
    ):

        for cls in symbols.get(
            "classes",
            []
        ):

            context = self._get_context(
                source_code,
                cls["start_line"]
            )

            if "@Service" in context:

                cls[
                    "framework"
                ] = "SpringBoot"

                cls[
                    "component_type"
                ] = "SERVICE"

    # =====================================================
    # REPOSITORIES
    # =====================================================

    def _detect_spring_repositories(
        self,
        symbols,
        source_code
    ):

        for cls in symbols.get(
            "classes",
            []
        ):

            context = self._get_context(
                source_code,
                cls["start_line"]
            )

            if "@Repository" in context:

                cls[
                    "framework"
                ] = "SpringBoot"

                cls[
                    "component_type"
                ] = "REPOSITORY"

    # =====================================================
    # COMPONENTS
    # =====================================================

    def _detect_spring_components(
        self,
        symbols,
        source_code
    ):

        for cls in symbols.get(
            "classes",
            []
        ):

            context = self._get_context(
                source_code,
                cls["start_line"]
            )

            if "@Component" in context:

                cls[
                    "framework"
                ] = "SpringBoot"

                cls[
                    "component_type"
                ] = "COMPONENT"

    # =====================================================
    # REQUEST MAPPINGS
    # =====================================================

    def _detect_request_mappings(
        self,
        symbols,
        source_code
    ):

        mapping_patterns = [

            (
                "@GetMapping",
                "GET"
            ),

            (
                "@PostMapping",
                "POST"
            ),

            (
                "@PutMapping",
                "PUT"
            ),

            (
                "@DeleteMapping",
                "DELETE"
            ),

            (
                "@PatchMapping",
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

            for annotation, method in mapping_patterns:

                if annotation not in context:
                    continue

                function[
                    "framework"
                ] = "SpringBoot"

                function[
                    "component_type"
                ] = "API_ENDPOINT"

                function[
                    "http_method"
                ] = method

                route_match = re.search(
                    rf"{annotation}\(\"([^\"]+)\"\)",
                    context
                )

                if route_match:

                    function[
                        "route"
                    ] = route_match.group(
                        1
                    )

            if (
                "@RequestMapping"
                in context
            ):

                function[
                    "framework"
                ] = "SpringBoot"

                function[
                    "component_type"
                ] = "API_ENDPOINT"

    # =====================================================
    # JPA ENTITIES
    # =====================================================

    def _detect_jpa_entities(
        self,
        symbols,
        source_code
    ):

        for cls in symbols.get(
            "classes",
            []
        ):

            context = self._get_context(
                source_code,
                cls["start_line"]
            )

            if (
                "@Entity"
                in context
            ):

                cls[
                    "framework"
                ] = "SpringBoot"

                cls[
                    "component_type"
                ] = "ENTITY"

            if (
                "@Table"
                in context
            ):

                cls[
                    "framework"
                ] = "SpringBoot"

                cls[
                    "component_type"
                ] = "DATABASE_MODEL"