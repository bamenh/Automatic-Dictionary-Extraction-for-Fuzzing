import angr
import sys
import os

def extract_dictionary(binary_path, output_dict):
    print(f"[*] Initialize Angr Project file: {binary_path}")
    project = angr.Project(binary_path, auto_load_libs=False)
    
    targets = [b"Path 1", b"Path 2", b"Path 3"]
    found_tokens = []

    for target in targets:
        print(f"[*] Using Z3 Solver to Symbolic Execution...: {target.decode()} ...")
        initial_state = project.factory.entry_state()
        simgr = project.factory.simulation_manager(initial_state)
        
        simgr.explore(find=lambda s, t=target: t in s.posix.dumps(1))
        
        if simgr.found:
            found_state = simgr.found[0]
            magic_bytes = found_state.posix.dumps(0)
            
            clean_str = magic_bytes.decode('utf-8', errors='ignore').strip('\x00')
            found_tokens.append(clean_str)
            print(f"  [+] Successful! Magic Bytes: '{clean_str}'")
        else:
            print(f"  [-] Stuck in {target.decode()}")

    with open(output_dict, "w") as f:
        for i, token in enumerate(found_tokens):
            f.write(f'token_{i+1}="{token}"\n')
            
    print(f"\n[+] All Dictionary Saved: {output_dict}")

if __name__ == "__main__":
    target_bin = "target/test_bin"
    output_file = "output/router.dict"
    
    if not os.path.exists(target_bin):
        print(f"Erorr: Not found {target_bin}. Compile C first!.")
        sys.exit(1)
        
    extract_dictionary(target_bin, output_file)
