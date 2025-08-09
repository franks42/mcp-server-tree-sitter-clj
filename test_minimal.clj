(defn- tool-nrepl-connect
  "Connect to nREPL server"
  [{:keys [host port]}]
  (let [host (or host "localhost")
        port (or port (discover-nrepl-port (get-in @state [:config :workspace])))]
    (if port
      (let [result (connect-to-nrepl host port)]
        (if (:success result)
          {:content [{:type "text"
                     :text (str "✅ Connected to nREPL at " host ":" port)}]}
          {:content [{:type "text" 
                     :text (str "❌ Connection failed: " (:error result))}]
           :isError true}))
      {:content [{:type "text"
                 :text "❌ No port specified and could not discover .nrepl-port file"}]
       :isError true})))

(defn- tool-nrepl-eval
  "Evaluate Clojure code via nREPL"
  [{:keys [code session ns]}]
  (let [conn-result (ensure-nrepl-connection)]
    (if (:success conn-result)
      (println "success")
      (println "error"))))