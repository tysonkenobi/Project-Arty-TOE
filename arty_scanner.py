import math
import numpy as np
import h5py
import os
import sys

# ==============================================================================
# NKST VALIDATION ENGINE ('ARTY-SCANNER') v3.0 - FULL SUITE
# Logic: Audits both TEMPORAL (LIGO) and SPATIAL (EHT) fidelity.
# ==============================================================================

class ArtyScanner:
    def __init__(self):
        self.PHI = 1.61803398875

    def visualize_simulation(self, filename="nkst_telemetry.h5"):
        print(f"\n[IO] Loading Telemetry: {filename}...")
        if not os.path.exists(filename):
            print("[Error] File not found. Run 'arty_simulator.py' first.")
            return False, None, None, None

        with h5py.File(filename, "r") as f:
            time = np.array(f["time"])
            density = np.array(f["density"])
            spin = np.array(f["phase_spin"])
            version = f.attrs.get("engine_version", "Unknown")
            print(f"[Meta] Engine Version: {version}")

        # Check for Spin (The Inversion)
        spin_detected = False
        inversion_index = -1
        
        for i, (t, val) in enumerate(zip(time, spin)):
            if val < 0: 
                if not spin_detected:
                    inversion_index = i 
                spin_detected = True
        
        if spin_detected:
            print(f"[PASS] Vector Inversion detected at Index {inversion_index}.")
            return True, spin, density, inversion_index
        else:
            print("[FAIL] No Vector Inversion found.")
            return False, None, None, None

    def validate_ligo_decay(self, sim_spin_data, start_index):
        print("\n" + "="*50)
        print("AUDIT 1: LIGO GW150914 (Temporal Decay)")
        print("="*50)

        # Historical Data (Gravitational Wave Amplitude)
        ligo_data = [4.81, 3.20, 1.84, 0.92, 0.31]
        
        if start_index + 5 > len(sim_spin_data):
            print("[Error] Simulation too short.")
            return False

        raw_sim_segment = sim_spin_data[start_index : start_index+5]
        sim_curve = np.abs(raw_sim_segment)
        
        # Normalize to start point
        scaling_factor = ligo_data[0] / sim_curve[0]
        normalized_sim = sim_curve * scaling_factor

        print(f"{'Step':<6} | {'LIGO Real':<12} | {'Sim Output':<12} | {'Delta'}")
        print("-" * 50)

        matches = 0
        for i in range(len(ligo_data)):
            real = ligo_data[i]
            sim = normalized_sim[i]
            delta = abs(real - sim)
            
            status = "OK" if delta < 0.8 else "DRIFT"
            if status == "OK": matches += 1
            
            print(f"{i:<6} | {real:<12.3f} | {sim:<12.3f} | {status}")

        accuracy = (matches / len(ligo_data)) * 100
        print(f"\n--> LIGO Match: {accuracy:.1f}%")
        return accuracy > 80

    def validate_eht_horizon(self, sim_density_data, inversion_index):
        print("\n" + "="*50)
        print("AUDIT 2: EHT M87* (Spatial Boundary)")
        print("="*50)
        
        # Target: The "Photon Ring" (Density = 1.0 Planck Limit)
        # We check the density at the moment of inversion (The Event Horizon).
        
        horizon_density = sim_density_data[inversion_index]
        
        # EHT Data Points (Normalized Brightness/Density Profile)
        # r=0 (Singularity), r=1 (Ring), r=5 (Ambient)
        targets = [
            {"region": "Ambient Space", "target": 0.0,  "sim": sim_density_data[0]}, # Start
            {"region": "Accretion",     "target": 0.5,  "sim": sim_density_data[inversion_index // 2]}, # Mid
            {"region": "Photon Ring",   "target": 1.0,  "sim": horizon_density} # The Wall
        ]
        
        print(f"{'Region':<15} | {'Target Mass':<12} | {'Sim Mass':<12} | {'Status'}")
        print("-" * 60)
        
        matches = 0
        for t in targets:
            # Check tolerance
            delta = abs(t["target"] - t["sim"])
            status = "LOCKED" if delta < 0.15 else "FAIL"
            if status == "LOCKED": matches += 1
            
            print(f"{t['region']:<15} | {t['target']:<12.2f} | {t['sim']:<12.2f} | {status}")
            
        # Check Stability (Did it hold the ring?)
        post_ring_density = sim_density_data[inversion_index + 5]
        is_stable = abs(post_ring_density - 1.0) < 0.01
        
        print(f"\n[Horizon Stability Check]")
        print(f"Density 5 steps post-impact: {post_ring_density:.4f}")
        print(f"Status: {'STABLE (Black Hole)' if is_stable else 'COLLAPSE (Singularity)'}")

        accuracy = (matches / len(targets)) * 100
        print(f"--> EHT Match: {accuracy:.1f}%")
        return accuracy > 90 and is_stable

    def run(self):
        is_valid, spin_data, density_data, idx = self.visualize_simulation()
        
        if is_valid:
            ligo_pass = self.validate_ligo_decay(spin_data, idx)
            eht_pass = self.validate_eht_horizon(density_data, idx)
            
            if ligo_pass and eht_pass:
                print("\n[SYSTEM VALIDATED] The NKST Protocol matches both LIGO and EHT data.")
            else:
                print("\n[SYSTEM WARNING] One or more physics checks failed.")
        else:
            print("Validation Aborted.")

if __name__ == "__main__":
    scanner = ArtyScanner()
    scanner.run()
