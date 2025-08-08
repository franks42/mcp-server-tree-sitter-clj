;; Clojure Tree-Sitter Query Samples
;; Extracted from nvim-treesitter for MCP adaptation

;; Function definitions
(list_lit
  .
  ((sym_lit
    name: (sym_name) @_keyword.function.name)
    (#any-of? @_keyword.function.name "defn" "defn-" "fn" "fn*"))
  .
  (sym_lit)? @function.name
  .
  (str_lit)? @function.docstring
  .
  (vec_lit)? @function.params)

;; Namespace declarations  
(list_lit
  .
  (sym_lit) @_include
  (#eq? @_include "ns")
  .
  (sym_lit) @namespace.name)

;; Macro patterns
((sym_lit
  name: (sym_name) @function.macro)
  (#any-of? @function.macro
    "." ".." "->" "->>" "amap" "areduce" "as->" "assert"
    "binding" "bound-fn" "case" "comment" "cond" "cond->" "cond->>"
    "condp" "declare" "delay" "dosync" "dotimes" "doto" "defmacro"
    "defmethod" "defmulti" "defn" "defn-" "defonce" "defprotocol"
    "defrecord" "defstruct" "deftype" "doseq" "for" "future"
    "gen-class" "gen-interface" "if-let" "if-not" "import" "io!"
    "lazy-cat" "lazy-seq" "let" "letfn" "locking" "loop" "memfn"
    "proxy" "proxy-super" "pvalues" "refer-clojure" "reify" "sync"
    "time" "when" "when-first" "when-let" "when-not" "while"
    "with-bindings" "with-in-str" "with-loading-context"
    "with-local-vars" "with-open" "with-out-str" "with-precision"
    "with-redefs"))

;; Data structures
(vec_lit) @data.vector
(list_lit) @data.list  
(map_lit) @data.map
(set_lit) @data.set

;; Protocol/deftype patterns
(list_lit
  .
  (sym_lit) @_keyword
  (#any-of? @_keyword "defprotocol" "deftype" "defrecord" "extend-protocol" "extend-type")
  .
  (sym_lit) @type.name)

;; Threading macro patterns  
(list_lit
  .
  (sym_lit) @_thread
  (#any-of? @_thread "->" "->>")
  .
  _ @thread.initial
  (_ @thread.step)+)

;; Let binding patterns
(list_lit
  .
  (sym_lit) @_let
  (#eq? @_let "let")
  .
  (vec_lit) @let.bindings
  (_ @let.body)+)

;; Destructuring patterns in binding vectors
(vec_lit
  ((sym_lit) @binding.name
   _ @binding.value)+)

;; Map destructuring
(map_lit
  ((key_lit) @destructure.key
   (sym_lit) @destructure.binding)+)