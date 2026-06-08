import re

from rag.symbol_extractors.base_extractor import (
    BaseExtractor
)


class CppExtractor(
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

        self._detect_classes(
            symbols
        )

        self._detect_structs(
            symbols
        )

        self._detect_namespaces(
            symbols,
            source_code
        )

        self._detect_templates(
            symbols
        )

        self._detect_stl_usage(
            symbols
        )

        self._detect_header_dependencies(
            symbols,
            source_code
        )

        return symbols

    # =====================================================
    # CLASSES
    # =====================================================

    def _detect_classes(
        self,
        symbols
    ):

        for cls in symbols.get(
            "classes",
            []
        ):

            cls[
                "framework"
            ] = "CPP"

            cls[
                "component_type"
            ] = "CLASS"

    # =====================================================
    # STRUCTS
    # =====================================================

    def _detect_structs(
        self,
        symbols
    ):

        for struct in symbols.get(
            "structs",
            []
        ):

            struct[
                "framework"
            ] = "CPP"

            struct[
                "component_type"
            ] = "STRUCT"

    # =====================================================
    # NAMESPACES
    # =====================================================

    def _detect_namespaces(
        self,
        symbols,
        source_code
    ):

        namespace_pattern = re.compile(
            r"namespace\s+([A-Za-z_][A-Za-z0-9_]*)"
        )

        matches = namespace_pattern.findall(
            source_code
        )

        if not matches:
            return

        namespace_name = matches[0]

        for symbol in symbols.get(
            "all_symbols",
            []
        ):

            symbol[
                "namespace"
            ] = namespace_name

    # =====================================================
    # TEMPLATES
    # =====================================================

    def _detect_templates(
        self,
        symbols
    ):

        for function in symbols.get(
            "functions",
            []
        ):

            content = function.get(
                "content",
                ""
            )

            if "template<" in content:

                function[
                    "framework"
                ] = "CPP"

                function[
                    "component_type"
                ] = "TEMPLATE_FUNCTION"

        for cls in symbols.get(
            "classes",
            []
        ):

            content = cls.get(
                "content",
                ""
            )

            if "template<" in content:

                cls[
                    "framework"
                ] = "CPP"

                cls[
                    "component_type"
                ] = "TEMPLATE_CLASS"

    # =====================================================
    # STL USAGE
    # =====================================================

    def _detect_stl_usage(
        self,
        symbols
    ):

        stl_types = [

            "std::vector",
            "std::map",
            "std::unordered_map",
            "std::set",
            "std::unordered_set",
            "std::queue",
            "std::stack",
            "std::priority_queue",
            "std::string"
        ]

        for symbol in symbols.get(
            "all_symbols",
            []
        ):

            content = symbol.get(
                "content",
                ""
            )

            used = []

            for stl in stl_types:

                if stl in content:

                    used.append(
                        stl
                    )

            if used:

                symbol[
                    "stl_usage"
                ] = used

    # =====================================================
    # HEADER DEPENDENCIES
    # =====================================================

    def _detect_header_dependencies(
        self,
        symbols,
        source_code
    ):

        includes = []

        include_pattern = re.compile(
            r'#include\s*[<"]([^>"]+)[>"]'
        )

        for match in include_pattern.findall(
            source_code
        ):

            includes.append(
                match
            )

        for symbol in symbols.get(
            "all_symbols",
            []
        ):

            symbol[
                "includes"
            ] = includes