(defn- tool-nrepl-connect
  "Connect to nREPL server"  
  [{:keys [host port]}]
  (println "first function"))


;; Some spacing and comment


(defn- tool-nrepl-eval
  "Evaluate Clojure code via nREPL"
  [{:keys [code session ns]}]
  (println "second function"))