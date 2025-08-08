# Controllable Test Server Implementation Guide

## Overview

Based on research into Babashka's nREPL server capabilities, this guide provides detailed approaches for creating controllable test servers to simulate failure modes needed for timeout implementation testing.

## Babashka nREPL Server Limitations

**Critical Findings:**
- **No Interrupt Support**: GraalVM compilation removes interrupt capability
- **Limited Sessions**: "Fake" sessions - not true isolation
- **No Middleware Access**: `babashka.nrepl.middleware` not exposed in current version
- **Simplified Architecture**: Designed for development, not complex failure simulation

## Three Approaches for Controllable Test Servers

### 1. Custom Test Server (Recommended)

**Best for**: Complete control, complex failure scenarios, deterministic testing

```clojure
(ns custom-test-nrepl
  (:require [clojure.core.async :as async])
  (:import [java.net ServerSocket Socket]
           [java.io BufferedReader InputStreamReader PrintWriter]))

;; Comprehensive test configuration
(defonce test-config 
  (atom {:delay-ms 0                    ; Response delay
         :simulate-hang false           ; Never send "done" 
         :network-partition false       ; Drop all responses
         :drop-probability 0.0          ; Random message dropping
         :corrupt-responses false       ; Send malformed data
         :memory-pressure false         ; Simulate OOM
         :connection-errors false       ; Socket errors
         :partial-responses false       ; Incomplete messages
         :message-count 0              ; Statistics
         :active-sessions #{}}))       ; Session tracking

;; Enhanced message handlers with failure modes
(defn handle-eval [msg]
  (let [config @test-config]
    (swap! test-config update :message-count inc)
    
    (cond
      ;; Network partition - completely silent
      (:network-partition config) 
      nil
      
      ;; Random message dropping
      (< (rand) (:drop-probability config))
      (do (println "💀 DROPPING message:" (:id msg)) nil)
      
      ;; Memory pressure simulation
      (:memory-pressure config)
      {:id (:id msg) :err "OutOfMemoryError: Java heap space" :status ["done"]}
      
      ;; Connection errors
      (:connection-errors config)
      (throw (java.io.IOException. "Connection reset by peer"))
      
      ;; Corrupt responses
      (:corrupt-responses config)
      {:id (:id msg) :corrupted-field "invalid-bencode-data" :status ["done"]}
      
      ;; Partial responses (missing required fields)
      (:partial-responses config)
      {:id (:id msg) :value "incomplete"}  ; Missing :status
      
      ;; Delay injection
      (> (:delay-ms config) 0)
      (do (Thread/sleep (:delay-ms config))
          {:id (:id msg) :value (str "Delayed result: " (eval-safe (:code msg))) :status ["done"]})
      
      ;; Hang simulation (missing "done" status)
      (:simulate-hang config)
      {:id (:id msg) :value (str "Hanging: " (eval-safe (:code msg)))}
      
      ;; Normal operation
      :else
      {:id (:id msg) :value (str (eval-safe (:code msg))) :status ["done"]})))

;; Safe evaluation with error handling
(defn eval-safe [code]
  (try
    (eval (read-string code))
    (catch Exception e (.getMessage e))))

;; Advanced control operations
(def control-operations
  {"test-slow-death"     #(gradual-slowdown 5000 60000)      ; Gradually slower
   "test-memory-leak"    #(simulate-memory-pressure true)     ; Memory exhaustion
   "test-connection-flap" #(connection-flapping 10)          ; Intermittent failures  
   "test-cascade-failure" #(cascade-failure-sequence)        ; Multiple failure modes
   "test-recovery-stress" #(recovery-stress-test 100)})      ; Rapid failure/recovery

;; Complex failure scenarios
(defn gradual-slowdown [start-delay max-delay]
  "Gradually increase response times to simulate degrading performance"
  (future
    (loop [delay start-delay]
      (when (< delay max-delay)
        (swap! test-config assoc :delay-ms delay)
        (Thread/sleep 5000)  ; Increase delay every 5 seconds
        (recur (min max-delay (* delay 1.2)))))))

(defn connection-flapping [cycles]
  "Alternate between working and failing connections"
  (future
    (dotimes [_ cycles]
      (swap! test-config assoc :connection-errors true)
      (Thread/sleep 2000)
      (swap! test-config assoc :connection-errors false) 
      (Thread/sleep 3000))))

(defn cascade-failure-sequence []
  "Simulate cascading failures: slow → hang → partition → recovery"
  (future
    (println "🔥 Starting cascade failure sequence...")
    ;; Phase 1: Gradual slowdown
    (swap! test-config assoc :delay-ms 2000)
    (Thread/sleep 10000)
    ;; Phase 2: Operations start hanging  
    (swap! test-config assoc :simulate-hang true)
    (Thread/sleep 15000)
    ;; Phase 3: Complete network partition
    (swap! test-config assoc :network-partition true)
    (Thread/sleep 10000)
    ;; Phase 4: Recovery
    (reset! test-config {:delay-ms 0 :simulate-hang false 
                         :network-partition false :message-count 0})
    (println "✅ Cascade failure sequence completed")))

;; Statistics and monitoring
(defn get-server-stats []
  (let [config @test-config]
    {:uptime-seconds (/ (- (System/currentTimeMillis) start-time) 1000)
     :messages-processed (:message-count config)
     :active-failure-modes (filter second (select-keys config 
                                            [:delay-ms :simulate-hang 
                                             :network-partition :drop-probability]))
     :current-config config}))
```

### 2. Wrapper-Based Control (Intermediate)

**Best for**: Using existing bb-nrepl with external control, simpler setup

```clojure
(ns bb-nrepl-wrapper
  (:require [babashka.nrepl.server :as nrepl-server]
            [clojure.core.async :as async]))

;; Proxy wrapper around bb-nrepl server
(defonce wrapped-server (atom nil))
(defonce control-config (atom {:intercept-requests false
                               :intercept-responses false  
                               :failure-modes {}}))

;; Request/Response interception
(defn intercept-nrepl-message [message direction]
  "Intercept and potentially modify nREPL messages"
  (let [config @control-config
        failure-modes (:failure-modes config)]
    (cond
      ;; Drop messages based on probability
      (and (= direction :request) 
           (< (rand) (:drop-request-probability failure-modes 0)))
      (do (println "🚫 Dropping request:" (:id message)) nil)
      
      ;; Inject delays
      (and (= direction :response)
           (> (:response-delay-ms failure-modes 0) 0))
      (do (Thread/sleep (:response-delay-ms failure-modes))
          message)
      
      ;; Corrupt messages  
      (and (:corrupt-responses failure-modes false)
           (= direction :response))
      (assoc message :corrupted-field "test-corruption")
      
      :else message)))

;; Start wrapper server with interception
(defn start-wrapped-server [port]
  (let [base-server (nrepl-server/start-server! {:port port :quiet true})
        control-port (+ port 1000)]
    
    ;; Start control HTTP server
    (start-control-server control-port)
    
    (reset! wrapped-server 
            {:base-server base-server
             :control-port control-port 
             :intercept-active true})
    
    (println "🎛️ Wrapped nREPL server running on port" port)
    (println "🕹️ Control interface on port" control-port)
    @wrapped-server))

;; HTTP control interface  
(defn start-control-server [port]
  (future
    ;; Simple HTTP server for control commands
    ;; POST /scenario/slow-5s
    ;; POST /scenario/network-partition
    ;; GET /status
    ;; POST /reset
    ))
```

### 3. Environment-Based Control (Simplest)

**Best for**: Basic failure modes, simple testing, CI integration

```clojure
(ns env-controlled-nrepl
  (:require [babashka.nrepl.server :as nrepl-server]))

;; Environment variable based configuration
(defn get-test-config []
  {:delay-ms (parse-int (or (System/getenv "NREPL_TEST_DELAY") "0"))
   :simulate-hang (= "true" (System/getenv "NREPL_TEST_HANG"))
   :drop-probability (parse-double (or (System/getenv "NREPL_TEST_DROP") "0.0"))
   :network-partition (= "true" (System/getenv "NREPL_TEST_PARTITION"))})

;; Wrapper functions that check environment
(defn env-controlled-eval [code]
  (let [config (get-test-config)]
    (when (> (:delay-ms config) 0)
      (Thread/sleep (:delay-ms config)))
    
    (when (:network-partition config)
      (throw (java.io.IOException. "Simulated network partition")))
    
    (when (< (rand) (:drop-probability config))
      (throw (java.io.IOException. "Simulated message drop")))
    
    ;; Normal evaluation
    (eval (read-string code))))

;; Start server with environment-based control
(defn start-env-controlled-server [port]
  (println "🌍 Starting environment-controlled nREPL server")
  (println "📋 Control via environment variables:")
  (println "   NREPL_TEST_DELAY=5000     # 5 second delays")
  (println "   NREPL_TEST_HANG=true      # Hanging operations") 
  (println "   NREPL_TEST_DROP=0.3       # 30% message drop rate")
  (println "   NREPL_TEST_PARTITION=true # Network partition")
  
  (let [config (get-test-config)]
    (println "🔧 Active configuration:" config))
  
  (nrepl-server/start-server! {:port port}))
```

## Testing Integration Examples

### Phase 1: Basic Timeout Testing

```bash
# Environment-based testing
NREPL_TEST_DELAY=30000 bb start-test-server &
bb test-timeout-basic  # Should timeout gracefully

NREPL_TEST_HANG=true bb start-test-server &  
bb test-hang-detection  # Should detect hanging operations

# Custom server testing  
bb start-custom-test-server --port 7890 &
bb test-control --scenario "slow-30s"
bb test-timeout-implementation
```

### Phase 2: Concurrent Operations

```bash
# Test message routing under stress
bb test-control --scenario "unreliable-30%"
bb test-concurrent-routing-100-ops

# Test routing with mixed failure modes
bb test-control --scenario "cascade-failure" 
bb test-routing-during-cascade
```

### Phase 3: Send Queue Testing

```bash
# Test send queue backpressure
bb flood-test --messages 10000 --rate 1000/sec

# Test send timeout handling
bb test-control --scenario "network-partition"
bb test-send-timeout-recovery
```

## Production Deployment Considerations

### Security
- **Disable in Production**: Test control must be disabled in production
- **Access Control**: Control interfaces need authentication
- **Resource Limits**: Prevent DoS through control API

### Monitoring Integration
```clojure
;; Integration with monitoring systems
(defn report-test-metrics [scenario results]
  {:test-scenario scenario
   :duration-ms (:duration results)
   :success-rate (:success-rate results) 
   :error-types (:error-distribution results)
   :timestamp (System/currentTimeMillis)})
```

### CI/CD Integration
```bash
#!/bin/bash
# Automated test pipeline

echo "🧪 Starting timeout implementation test suite"

# Phase 1 tests
for scenario in "normal" "slow-5s" "slow-30s" "hang" "network-partition"; do
    echo "Testing Phase 1 with scenario: $scenario"
    bb test-control --scenario "$scenario"
    bb test-phase-1 --timeout-ms 10000
    bb test-control --reset
done

# Collect results
bb generate-test-report --phase 1 --output phase1-results.json
```

## Conclusion

**Recommendation**: Use the **Custom Test Server approach** for comprehensive timeout implementation testing because:

1. **Complete Control**: Every failure mode can be precisely simulated
2. **Deterministic**: Same inputs always produce same failure patterns  
3. **Complex Scenarios**: Can simulate real-world cascading failures
4. **Performance Testing**: Measure timeout system overhead accurately
5. **Integration Validation**: Test against realistic nREPL behavior

The custom server provides the controlled environment needed to validate each phase of the timeout implementation plan with confidence.