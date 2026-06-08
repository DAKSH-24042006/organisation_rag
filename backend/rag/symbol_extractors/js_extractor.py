import re

from rag.symbol_extractors.base_extractor import (
    BaseExtractor
)


class JavaScriptExtractor(
    BaseExtractor
):

    def extract(
        self,
        tree,
        source_code,
        file_path=None
    ):

        print(
            "\n[JS EXTRACTOR LOADED]\n"
        )

        symbols = super().extract(
            tree,
            source_code,
            file_path=file_path
        )

        print(
            "[JS] Functions before fix:",
            [
                f.get("name")
                for f in symbols.get(
                    "functions",
                    []
                )
            ]
        )

        self._fix_function_names(
            symbols,
            source_code
        )

        self._filter_callback_functions(
            symbols
        )

        self._detect_react_components(
            symbols
        )

        self._detect_react_hooks(
            symbols
        )

        self._detect_nextjs_routes(
            symbols
        )

        self._detect_redux_slices(
            symbols
        )

        self._detect_context_providers(
            symbols
        )

        print(
            "[JS] Final Functions:",
            [
                f.get("name")
                for f in symbols.get(
                    "functions",
                    []
                )
            ]
        )

        return symbols

    # =====================================================
    # FIX FUNCTION NAMES
    # =====================================================

    def _fix_function_names(
        self,
        symbols,
        source_code
    ):

        source_lines = source_code.splitlines()

        for function in symbols.get(
            "functions",
            []
        ):

            print(
                "\n[JS FUNCTION]",
                function.get(
                    "name"
                )
            )

            start_line = max(
                0,
                function.get(
                    "start_line",
                    1
                ) - 3
            )

            end_line = min(
                start_line + 10,
                len(source_lines)
            )

            context = "\n".join(
                source_lines[
                    start_line:end_line
                ]
            )

            print(
                "[CONTEXT]\n",
                context[:300]
            )

            patterns = [

                r"const\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\([^)]*\)\s*=>",

                r"const\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*async\s*\([^)]*\)\s*=>",

                r"function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(",

                r"export\s+default\s+function\s+([A-Za-z_][A-Za-z0-9_]*)",

                r"export\s+const\s+([A-Za-z_][A-Za-z0-9_]*)"
            ]

            for pattern in patterns:

                match = re.search(
                    pattern,
                    context
                )

                if match:

                    print(
                        "[MATCH FOUND]",
                        match.group(1)
                    )

                    function[
                        "name"
                    ] = match.group(
                        1
                    )

                    break

        print(
            "\n[JS] Functions after fix:",
            [
                f.get("name")
                for f in symbols.get(
                    "functions",
                    []
                )
            ]
        )

    # =====================================================
    # FILTER CALLBACKS
    # =====================================================

    def _filter_callback_functions(
        self,
        symbols
    ):

        filtered = []

        ignored = {

            "e",
            "event",
            "item",
            "data",
            "result",
            "response",
            "res",
            "req",
            "params",
            "param",
            "l",
            "i",
            "x",
            "y"
        }

        for function in symbols.get(
            "functions",
            []
        ):

            name = function.get(
                "name",
                ""
            )

            if name in ignored:
                continue

            if len(name) == 1:
                continue

            filtered.append(
                function
            )

        symbols[
            "functions"
        ] = filtered

    # =====================================================
    # REACT COMPONENTS
    # =====================================================

    def _detect_react_components(
        self,
        symbols
    ):

        components = []

        for function in symbols.get(
            "functions",
            []
        ):

            name = function.get(
                "name",
                ""
            )

            content = function.get(
                "content",
                ""
            )

            is_component = False

            if (
                name
                and
                name[0].isupper()
            ):
                is_component = True

            if "return (" in content:
                is_component = True

            if "<div" in content:
                is_component = True

            if "useState(" in content:
                is_component = True

            if is_component:

                function[
                    "framework"
                ] = "React"

                function[
                    "component_type"
                ] = "COMPONENT"

                components.append(
                    function
                )

        symbols[
            "react_components"
        ] = components

    # =====================================================
    # REACT HOOKS
    # =====================================================

    def _detect_react_hooks(
        self,
        symbols
    ):

        hooks = {

            "useState",
            "useEffect",
            "useMemo",
            "useCallback",
            "useReducer",
            "useRef",
            "useContext"
        }

        for function in symbols.get(
            "functions",
            []
        ):

            content = function.get(
                "content",
                ""
            )

            found = []

            for hook in hooks:

                if hook in content:
                    found.append(
                        hook
                    )

            if found:

                function[
                    "framework"
                ] = "React"

                function[
                    "hooks"
                ] = found

    # =====================================================
    # NEXTJS
    # =====================================================

    def _detect_nextjs_routes(
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

            if "NextResponse" in content:

                function[
                    "framework"
                ] = "NextJS"

                function[
                    "component_type"
                ] = "API_ROUTE"

    # =====================================================
    # REDUX
    # =====================================================

    def _detect_redux_slices(
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

            if "createSlice(" in content:

                function[
                    "framework"
                ] = "Redux"

                function[
                    "component_type"
                ] = "SLICE"

    # =====================================================
    # CONTEXT PROVIDERS
    # =====================================================

    def _detect_context_providers(
        self,
        symbols
    ):

        for function in symbols.get(
            "functions",
            []
        ):

            name = function.get(
                "name",
                ""
            )

            content = function.get(
                "content",
                ""
            )

            if (
                "createContext("
                in content
                or
                name.endswith(
                    "Provider"
                )
            ):

                function[
                    "framework"
                ] = "React"

                function[
                    "component_type"
                ] = "CONTEXT_PROVIDER"