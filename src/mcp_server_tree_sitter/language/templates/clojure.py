"""Query templates for Clojure."""

TEMPLATES = {
    "functions": """
        ;; Public function definitions
        (list_lit
          .
          (sym_lit) @_defn
          (#eq? @_defn "defn")
          .
          (sym_lit) @function.name
          .
          (str_lit)? @function.docstring
          .
          (vec_lit)? @function.params) @function.def

        ;; Private function definitions
        (list_lit
          .
          (sym_lit) @_defn
          (#eq? @_defn "defn-")
          .
          (sym_lit) @function.name
          .
          (str_lit)? @function.docstring
          .
          (vec_lit)? @function.params) @function.def

        ;; Lambda functions
        (list_lit
          .
          (sym_lit) @_fn
          (#any-of? @_fn "fn" "fn*")
          .
          (vec_lit)? @function.params) @function.def
    """,
    "namespaces": """
        ;; Namespace declarations
        (list_lit
          .
          (sym_lit) @_ns
          (#eq? @_ns "ns")
          .
          (sym_lit) @namespace.name) @namespace.def
    """,
    "imports": """
        ;; Require statements
        (list_lit
          .
          (sym_lit) @_require
          (#eq? @_require "require")
          .
          (_) @import.module) @import

        ;; Import statements  
        (list_lit
          .
          (sym_lit) @_import
          (#eq? @_import "import")
          .
          (_) @import.class) @import

        ;; Use statements
        (list_lit
          .
          (sym_lit) @_use
          (#eq? @_use "use")
          .
          (_) @import.module) @import
    """,
    "macros": """
        ;; Macro definitions
        (list_lit
          .
          (sym_lit) @_defmacro
          (#eq? @_defmacro "defmacro")
          .
          (sym_lit) @macro.name
          .
          (str_lit)? @macro.docstring
          .
          (vec_lit)? @macro.params) @macro.def

        ;; Threading macros
        (list_lit
          .
          (sym_lit) @_thread
          (#any-of? @_thread "->" "->>")
          .
          _ @thread.initial
          (_ @thread.step)+) @thread.macro
    """,
    "protocols": """
        ;; Protocol definitions
        (list_lit
          .
          (sym_lit) @_defprotocol
          (#eq? @_defprotocol "defprotocol")
          .
          (sym_lit) @protocol.name) @protocol.def

        ;; Record definitions
        (list_lit
          .
          (sym_lit) @_defrecord
          (#eq? @_defrecord "defrecord")
          .
          (sym_lit) @record.name) @record.def

        ;; Type definitions
        (list_lit
          .
          (sym_lit) @_deftype
          (#eq? @_deftype "deftype")
          .
          (sym_lit) @type.name) @type.def

        ;; Protocol implementations
        (list_lit
          .
          (sym_lit) @_extend
          (#any-of? @_extend "extend-protocol" "extend-type")
          .
          (sym_lit) @extend.protocol) @extend.def
    """,
    "bindings": """
        ;; Let bindings
        (list_lit
          .
          (sym_lit) @_let
          (#eq? @_let "let")
          .
          (vec_lit) @let.bindings
          (_ @let.body)+) @let.def

        ;; Binding vectors
        (vec_lit
          ((sym_lit) @binding.name
           _ @binding.value)+) @binding.vector

        ;; Map destructuring
        (map_lit
          ((key_lit) @destructure.key
           (sym_lit) @destructure.binding)+) @destructure.map
    """,
    "data_structures": """
        ;; Vectors
        (vec_lit) @data.vector

        ;; Lists (function calls)
        (list_lit) @data.list

        ;; Maps
        (map_lit) @data.map

        ;; Sets
        (set_lit) @data.set
    """,
    "atoms": """
        ;; Atom operations
        (list_lit
          .
          (sym_lit) @_atom_op
          (#any-of? @_atom_op "swap!" "reset!" "compare-and-set!")
          .
          (sym_lit) @atom.name) @atom.operation

        ;; Atom dereferencing
        (deref_lit
          (sym_lit) @atom.deref) @atom.access
    """,
    "function_calls": """
        ;; Function calls (any list starting with a symbol)
        (list_lit
          .
          (sym_lit) @call.function
          (_ @call.arg)*) @call
    """,
}
