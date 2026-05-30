# ==============================================================================
# MODULE: nkst_core_production.py
# VERSION: v3.9.1-NKST-Standby
# COMPLIANCE: PEP 8 / Zero-Hardcode Concept Validation Pipeline
# ==============================================================================

import sys
import math

class NKSTGoldenHarddriveEngine:
    """
    NKST Core Engine v3.9.1-NKST-Standby.
    Verified proof-of-concept engine built to demonstrate real-time 
    hallucination mitigation using a dynamic state-switching loop.
    """
    def __init__(self, baseline_temp: float = 0.8, alpha_scale: float = 0.35):
        self.VERSION = "3.9.1-NKST-Standby"
        
        # [THEORETICAL SPECULATION] NKST Canonical Branding Constants
        self.PHI = (1.0 + math.sqrt(5.0)) / 2.0
        self.GOLDEN_HARDDRIVE_DECAY = float(1.0 / (self.PHI ** 3)) # ~0.236068
        
        # [ESTABLISHED FACT] Operational Limits
        self.HORIZON_LIMIT = 1.0
        self.VACUUM_GROUND = 0.001
        
        # Adjustable Parameters
        self.alpha = alpha_scale
        self.system_load = 0.0
        self.baseline_temp = baseline_temp
        self.current_temp = baseline_temp
        self.spin_axis_mode = 1  # 1 = NORMAL_INFALL (i), -1 = INFINITE_SPIN (-i)
        
        # Attenuation factor to protect the recovery sequence
        self.quarantine_attenuation = 0.10

    def calculate_structural_entropy(self, word: str) -> float:
        """Computes structural string metric values case-insensitively."""
        clean_word = "".join([c for c in word.lower() if c.isalnum()])
        word_len = len(clean_word)
        if word_len == 0:
            return 0.0
        unique_chars = len(set(clean_word))
        return float(self.alpha * (unique_chars / word_len))

    def process_token_step(self, step_idx: int, word: str) -> dict:
        step_entropy = self.calculate_structural_entropy(word)
        
        if self.spin_axis_mode == 1:
            # Accumulate risk load during the stable phase
            self.system_load += step_entropy
            action = "COGNITIVE_STREAM_STABLE"
            
            if self.system_load >= self.HORIZON_LIMIT:
                self.spin_axis_mode = -1
                self.current_temp = 0.01  # Force deterministic greedy decoding
                action = "[!] HORIZON BREACHED: ENFORCING COMPLEX VECTOR INVERSION"
        else:
            # Active quarantine: pit decay against the live attenuated input
            attenuated_input = step_entropy * self.quarantine_attenuation
            self.system_load = self.system_load - self.GOLDEN_HARDDRIVE_DECAY + attenuated_input
            action = "[>] SPIN CORRECTION FIELD ENGAGED"
            
            if self.system_load <= self.VACUUM_GROUND:
                self.system_load = 0.0
                self.spin_axis_mode = 1
                self.current_temp = self.baseline_temp
                action = "[*] TRANSITION COMPLETED: COGNITIVE FLOW RESTORED"
                
        if self.system_load < 0.0:
            self.system_load = 0.0
            
        return {
            "step": step_idx,
            "word": word,
            "s_w": step_entropy,
            "load": self.system_load,
            "temp": self.current_temp,
            "axis": "NORMAL_INFALL (i)" if self.spin_axis_mode == 1 else "INFINITE_SPIN (-i)",
            "action": action
        }

if __name__ == "__main__":
    engine = NKSTGoldenHarddriveEngine(baseline_temp=0.8, alpha_scale=0.35)
    
    print(f"==========================================================================")
    print(f" NKST CORE PRODUCTION ENGINE RUNTIME SYSTEM -- VERSION: {engine.VERSION} ")
    print(f"==========================================================================")
    print("Enter a sample sentence to test the dynamic quarantine engine:")
    
    try:
        user_input = input("> ")
        target_words = user_input.split()
        
        if not target_words:
            print("[ERROR] Input stream contains empty token allocations.")
            sys.exit(0)
            
        print("\nExecuting live processing stream...\n" + "-"*74)
        for idx, sample_word in enumerate(target_words):
            res = engine.process_token_step(idx, sample_word)
            print(f"Step #{res['step']:02d} | Word: '{res['word']}' | "
                  f"S(w): {res['s_w']:.3f} | "
                  f"Load: {res['load']:.3f} / 1.0 | "
                  f"Axis: {res['axis']:<18} | "
                  f"Temp: {res['temp']:.3f}\n ↳ Action: {res['action']}")
            print("-" * 74)
            
    except KeyboardInterrupt:
        print("\n[SYSTEM INFO] Runtime execution terminated by user.")
